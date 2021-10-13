# EDToken

EDToken is a simple way to execute commands that require tokens or sensitive
data stored through profiles. These profiles are a dictionaries that store our
information and so execute it in the future. However to store these, edtoken
encrypt them with AES-256 algorithm for mantain your tokens and sensiteves data
safe. 


## Installation

Install EDToken using:

    git clone https://github.com/thecoblack/edtoken.git
    python setup.py install

## Usage

Using EDToken is simple, firstly you need to create a profile where you save
all dictionaries values to execute the template.

    edtoken add <profilename>

Secondly, you need add a template, this should be a command that you want
execute in the future, some example could be:

    edtoken set <yourprofile> --temp "git push https://{?token}@github.com/{user}/yourcoolrepository.git"

As your can see, edtoke use a {key} to replace it for the key value, however to
mark that it is a key with a encrypted values, you need add a "?" in fron of
the key.

Now, it is time to set the values for {user} and {?token}.

    edtoken set <yourprofile> -k user -v tothemoon
    edtoken set <yourprofile> -k token -v <secret token> --sym <key to encrypt with AES-256>

Finally, you just have wait at the moment to use the command and execute the
following line.

    edtoken exec <yourprofile> --sym <key to decrypt>
