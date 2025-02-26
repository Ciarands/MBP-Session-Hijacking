# MovieBoxPro Session-Hijacking (15/05/2024)
*After correspondance with the MBP team the vulnerabilities described in this document have been resolved* :warning:

On 15 April 2024 <https://www.movieboxpro.app/> was victim to a user-enumeration attack, which leaked its 6 million user accounts emails via its "pay-on-behalf" route, with all of its customers emails ending up on <https://haveibeenpwned.com/>.

Due to this, I decided to take a slightly closer look at the applications security, which lead to the discovery of the attack described below:

## Demo 🎥

https://github.com/user-attachments/assets/26fb9b3d-80a1-4073-8177-8c865f80c288

## Overview :spiral_notepad:
Generating session-cookies locally by exploiting the platforms weak implementation of session cookies and formulating attacks based on this access.

## Intro :cinema:
MBP (MovieBoxPro) uses google for its authentication, a common feature used for simple and secure login, when implemented correctly; however this often isn't the case...

Logging on with MBP, it will set a "ui" cookie which is base64 encoded JSON with 3 parameters; `app_key`, `encrypt_data`, `verify`, this will be the focus of our attack.

## Attacking the session cookie :rage::cookie:
Immediately using cryptanalysis we can determine that the `encrypt_data` param is using an encryption called DES3 (Triple DES), so what is DES3?

DES3 is a symmetric-key block cipher, which applies the DES cipher algorithm three times to each data block using a 56-bit key, it has been retired since 2005 due to fears of being easily brute-forcible and has been long since replaced by AES (which in its own regards is slowly being phased out now).

With this knowledge there are 2 obvious avenues for attack, bruteforcing or digging deeper.

## Digging Deeper :detective:
Often you will see attacks which stem from mobile apps leaking information it really shouldn't, MBP also has an app, lets take a closer look.
Using a tool like [jadx](<https://github.com/skylot/jadx>) we can take their .apk and generate some Java 🤮, after looking around you may come across this in their apps `classes3.dex`:

![image](https://github.com/user-attachments/assets/7d91d9fb-47ef-4d0f-a40d-b6b5e2f440d1)

## Understanding The Java :thinking:
The `super` keyword in Java refers to superclass (parent) objects.
In this case, `com.movieboxpro.android.http.g` is the class in which encryption within the app takes place, using our intuition we can make the assumption that this could be how they also encrypt their session cookies.
As mentioned earlier DES3 is a symmetric-key block cipher, meaning it uses the same keys for encryption and decryption, we can try and use these keys to decrypt our `encrypt_data` param and if we can, our keys are a match!

Which in this case they are...

After decoding this parameter we can find even more JSON with the following keys:

- `uid`
-  `username`
-  `nickname`
-  `last_time`
-  `openid_type`
-  `openid`
-  `add_time`
-  `family`
-  `dead_time`
-  `appid`
-  `email`
-  `bind_gmail`
-  `notify_setting`
-  `invite_count`
-  `remark`
-  `reg_from`
-  `last_login_ip`
-  `amount`
-  `total_charge`
-  `disable`
-  `vip_traffic`
-  `ban_comment`
-  `hide_maybe_like`
-  `expired_date`

Interesting and potentially very exploitable, but at the current moment we first need to determine what `app_key` and `verify` do, as we decided to dig deeper, we can use the `g` class as reference determining that: 
- `app_key` is an md5 hashed `"moviebox"`
- `verify` is md5 hashed `app_key` + `ENCRYPTION_KEY` + `encrypt_data`
We now have complete ability to modify our session params.

## Modifying our session :vibration_mode:
As mentioned earlier MBP suffered a user-enumeration attack, this is a very simple attack to perform and usually is a result of poor implementation of user identifiers (usually numeric and incremental).
With this knowledge and seeing a `uid` param in the encrypted payload we can try to modify this to a seperate uid and see what happens, this is exactly what I did.

After stripping out identifiable info this is what I was left with:

![image](https://github.com/user-attachments/assets/465bef79-6146-4179-9fdb-415e2683afd9)

## And it worked :tada:
I had successfully generated a `ui` cookie which I could use to login to my account based on only my `uid` and a few other faked params.
Seeing as these params clearly weren't all validated, I began testing to see what actually was necessary to generate a "valid" cookie.

Through trial and error I discovered that only `uid` and `expired_date` were necessary to create a valid cookie!
- `uid` being an incremental integer for each of their 6 million users.
- `expired_date` being a Unix Epoch timestamp.

## Building on this attack :muscle:
After gaining creating an attack which could compromise 6 million user accounts, I came to the obvious conclusion... 

This wasn't powerful enough.

So I began seeing what I could do to create an exploit-chain, the juiciest target obviously being this button right here:
![image](https://github.com/user-attachments/assets/8a905e19-c6cb-48cc-b808-146471ad0ccb)

## Attacking The Account Deletion Feature :ghost:
When clicking this button it sends a confirmation email verifying that you really want to delete the account.

In this confirmation email it provides a link to <https://www.ravenedm.com/jump/click.html> with a `data` parameter...

Want to guess what this `data` parameter is?

Another session cookie!

We now not only had access to every single user account and all their personal info but could also arbitrarily delete their accounts instantly...
## Conclusion :gift:
MBP has now implemented a more secure JWT (JSON web token) based approach based on my advice, and I have been paid out for responsibly disclosing this exploit-chain as apart of their bug bounty programme.
