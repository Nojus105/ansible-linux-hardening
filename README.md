# Ansible Linux Hardening

Idempotent ansible roles for hardening an ubuntu server host (ssh, ufw, fail2ban, unattended-upgrades) and deploying an https nginx reverse proxy with python verification.

## What it configures

### `hardening` role
- Installs `ufw`, `fail2ban`, `python3-systemd`, and `unattended-upgrades`
- Deploys `/etc/ssh/sshd_config.d/00-hardening.conf` (key-only auth, no root login, `MaxAuthTries 3`) and validates with `sshd -t`
- Configures `/etc/fail2ban/jail.local` with the `systemd` backend and enables the `sshd` jail
- Allows tcp ports `22`, `80`, and `443`, then enables `ufw` with default incoming deny

### `nginx_proxy` role
- Generates a self-signed 2048-bit tls certificate in `/etc/nginx/ssl/` if missing
- Removes the default nginx site and deploys the reverse proxy config from `site.conf.j2`
- Redirects http (`80`) to https (`443`) with `301`, sets `X-Content-Type-Options` and `X-Frame-Options` headers, and checks syntax with `nginx -t` before reloading

## Project structure

```text
.
├── ansible.cfg
├── inventory/
│   └── hosts.ini
├── playbooks/
│   └── site.yml
├── roles/
│   ├── hardening/
│   │   ├── handlers/main.yml
│   │   └── tasks/main.yml
│   └── nginx_proxy/
│       ├── handlers/main.yml
│       ├── tasks/main.yml
│       └── templates/site.conf.j2
└── scripts/
    └── verify_server.py
```

## Prerequisites

- `ansible`, `python3`, and the `community.general` collection on the control machine:

```bash
ansible-galaxy collection install community.general
```

- An ubuntu server host with ssh key login configured
- Passwordless `sudo` for the ansible user on the target host:

```bash
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/ansible
sudo chmod 0440 /etc/sudoers.d/ansible
sudo visudo -cf /etc/sudoers.d/ansible
```

## Usage

1. Set your target ip and ssh user in `inventory/hosts.ini`:

```ini
[webservers]
lab-web ansible_host=192.168.122.57 ansible_user=ubuntu
```

2. Test ssh and sudo access:

```bash
ansible webservers -b -m ping
```

3. Run the playbook (run 2 times to confirm idempotency):

```bash
ansible-playbook playbooks/site.yml
```

4. Run the verification script:

```bash
python3 scripts/verify_server.py 192.168.122.57
```

## Verification output

### Idempotency check (2nd playbook run)

```text
PLAY RECAP *********************************************************************
lab-web                    : ok=14   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

### Endpoint and port checks

```text
[PASS] Port 22 is open on 192.168.122.57
[PASS] Port 80 is open on 192.168.122.57
[PASS] Port 443 is open on 192.168.122.57
[PASS] HTTP 80 redirects to https://192.168.122.57/
[PASS] HTTPS 443 returned 200: hardened nginx proxy online
```
