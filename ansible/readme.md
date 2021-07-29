## ansible to install meinsack.click on server

this was tested on Google f1.micro, AWS t3.nano and Hetzner vps

```
ansible-playbook setup.yml -l meinsack_server --vault-id vault_pass.txt
```

in vault_pass.txt is a password that is not checked in this repo!

This password is used to encrypt the DNS token for acme.sh.


### deploy/update current version

```
ansible-playbook setup.yml -l meinsack_server --tags "datasette"
```
