# PLUGIN

Plugins are additional components to add certain capabilities without having to change or rebuild the main system. Conceptually, a plugin can be thought of as an extension/module that extends the capabilities of the host application. The main application provides a mechanism or interface for plugins to “connect”, then plugins provide additional functions.

## Function Examples

In **Storm-Framework**, Plugins are used as new capabilities or new features, to change the behavior of how modules are executed up to the payloads sent. So this new capability is useful to use when doing Exploitation, OSINT, Recon, Scanning, etc. For instance, if executing a module and waiting for the result takes a significant amount of time, you can use a specialized plugin like `ringing`; this ensures that when important information is received, your device will automatically ring.

### How to use

​The plugin system uses a registry-based registration mechanism with a `load`/`unload` lifecycle and periodic integrity checks.

#### ORDER:

**load <plugin_name>**
- **Behavior:** Activate the plugin and register it in the registry.
- **Persistence:** Persistent. The framework automatically creates an active session, so the plugin will remain active even if you restart or exit.


**unload <plugin_name>**
- **Behavior:** Instantly deactivate plugins and clear active sessions immediately.

**show plugin** 
- **Behavior:** Displays the status table of all plugins (`ACTIVE`, `CRASHED`, `INACTIVE`, or `ORPHANED`).
- **Security Note (`ORPHANED` state):** This state detects if a plugin file is silently deleted by another process at runtime (the file is in memory but missing from disk). Integrity Check will trigger a warning when the framework is restarted as an indicator of tampering or manipulation of external files.
 
Show Plugin View:

```bash
┌─(storm<⚡>framework)-[~]
└─➤ show plugin

PLUGIN NAME               STATUS
------------------------------------
demo_plug                 INACTIVE
multi_decoder             INACTIVE
sendlog_service           ACTIVE

┌─(storm<⚡>framework)-[~]
└─➤
```
