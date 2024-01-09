<!-- markdownlint-disable -->

<a href="../src/tmate.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `tmate.py`
Configurations and functions to operate tmate-ssh-server. 

**Global Variables**
---------------
- **APT_DEPENDENCIES**
- **GIT_REPOSITORY_URL**
- **PORT**

---

<a href="../src/tmate.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `install_dependencies`

```python
install_dependencies() → None
```

Install dependenciese required to start tmate-ssh-server container. 



**Raises:**
 
 - <b>`DependencyInstallError`</b>:  if there was something wrong installing the apt package  dependencies. 


---

<a href="../src/tmate.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `install_keys`

```python
install_keys(host_ip: Union[IPv4Address, IPv6Address, str]) → None
```

Install key creation script and generate keys. 



**Args:**
 
 - <b>`host_ip`</b>:  The charm host's public IP address. 



**Raises:**
 
 - <b>`KeyInstallError`</b>:  if there was an error creating ssh keys. 


---

<a href="../src/tmate.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `start_daemon`

```python
start_daemon() → None
```

Install unit files and start daemon. 



**Raises:**
 
 - <b>`DaemonStartError`</b>:  if there was an error starting the tmate-ssh-server docker process. 


---

<a href="../src/tmate.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_fingerprints`

```python
get_fingerprints() → Fingerprints
```

Get fingerprint from generated keys. 



**Raises:**
 
 - <b>`IncompleteInitError`</b>:  if the keys have not been generated by the create_keys.sh script. 
 - <b>`KeyInstallError`</b>:  if there was something wrong generating fingerprints from public keys. 



**Returns:**
 The generated public key fingerprints. 


---

<a href="../src/tmate.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_tmate_conf`

```python
generate_tmate_conf(host: str) → str
```

Generate the .tmate.conf values from generated keys. 



**Args:**
 
 - <b>`host`</b>:  The host IP address. 



**Raises:**
 
 - <b>`FingerprintError`</b>:  if there was an error generating fingerprints from public keys. 



**Returns:**
 The tmate config file contents. 


---

## <kbd>class</kbd> `DaemonStartError`
Represents an error while starting tmate-ssh-server daemon. 





---

## <kbd>class</kbd> `DependencyInstallError`
Represents an error while installing dependencies. 





---

## <kbd>class</kbd> `FingerprintError`
Represents an error with generating fingerprints from public keys. 





---

## <kbd>class</kbd> `Fingerprints`
The public key fingerprints. 



**Attributes:**
 
 - <b>`rsa`</b>:  The RSA public key fingerprint. 
 - <b>`ed25519`</b>:  The ed25519 public key fingerprint. 





---

## <kbd>class</kbd> `IncompleteInitError`
The tmate-ssh-server has not been fully initialized. 





---

## <kbd>class</kbd> `KeyInstallError`
Represents an error while installing/generating key files. 




