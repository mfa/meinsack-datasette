## ansible to install meinsack.click on server

this was tested on Google f1.micro, AWS t3.nano and Hetzner vps with ArchLinux as Linux.  
The ArchLinux specific part is in the full system upgrade at the beginning and all the package installs in the ``setup.yml``


```
ansible-playbook setup.yml -l meinsack_server --vault-id vault_pass.txt
```

in vault_pass.txt is a password that is not checked in this repo!

This password is used to encrypt the DNS token for acme.sh.


### deploy/update current version

```
ansible-playbook setup.yml -l meinsack_server --tags "datasette"
```
