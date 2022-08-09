# EDToken

EDToken is a simple way to execute commands that require tokens or sensitive
data stored through profiles. These profiles are a dictionaries that store our
information and so execute it in the future. However to store these, edtoken
encrypt them with AES-256 algorithm for mantain your tokens and sensiteves data
safe. 


## Installation

Install EDToken using:

    git clone https://github.com/thecoblack/edtoken.git
    python setup.py install --user

## Usage

Using EDToken is simple, firstly you need to create a profile where you save
all dictionaries values to execute the template.

    edtoken profile add <profilename>

Secondly, you need add a template, this should be a command that you want
execute in the future, some example could be:

    edtoken profile set <yourprofile> --temp "git push https://{?token}@github.com/{user}/yourcoolrepository.git"

As you can see, edtoken use a {key} to replace it for the key value, however to
mark that it is a key with a encrypted values, you need add a "?" in fron of
the key.

Now, it is time to set the values for {user} and {?token}.

    edtoken profile set <yourprofile> -k user -v tothemoon
    edtoken profile set <yourprofile> -k token --sym

Finally, you just have wait at the moment to use the command and execute the
following line.

    edtoken profile exec <yourprofile> --sym


### Wallet 

Wallet function allows to the user replace parts of any file like "exec" command
with the templates, as explained above. For use this function, firsly we need to
set the file path with "file" key in your profile, with: 

    edtoken set <yourprofile> --file <file path>

Secondly, adds all the keys added within the file with the "set" command.
For example, if we have the following file content.

    Hi, i'm using {?token}

We will set the key "token" in the same way as templates keys. Once, we have
everything configured, we will use the "wallet" command to decrypt the parts of
the file.

    edtoken wallet open <yourprofile>

Or "wallet close" command to encrypt the file again.

    edtoken wallet close <yourprofile>