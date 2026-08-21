# Mobile and native

## The governing assumption

**Everything shipped in the binary is public.** Attackers unzip apps. Treat any
key, endpoint, or logic in the bundle as published. The only secrets on a mobile
client are the ones the user's own session issues.

This makes the most common mobile finding also the most serious: a key that is
"hidden" in an environment variable and then embedded at build time is not
hidden at all.

## Checklist by surface

### Secrets and configuration

- Public/anon keys only. A service-role or admin key in the app is CRITICAL.
- Environment variables prefixed for client exposure are compiled into the
  bundle. Confirm what each one contains.
- Session tokens live in the platform keychain/keystore, never in plain
  preferences or async storage.
- Source maps uploaded for error tracking must not be publicly served.

### Share extensions and app groups

Extensions are a separate process with a shared container. That container is the
trust boundary.

- What is written to the shared app group? Anything in it is readable by every
  extension in the group.
- If the extension needs an authenticated call, the token comes from a shared
  keychain item with the tightest possible access group — never copied into
  plain shared storage.
- Extensions have hard memory limits. Verify that failure is graceful and does
  not leave partial writes or a token in a temp file.
- Data received from the host app is untrusted input. It came from another
  application.

### Deep links and universal links

- Every deep link parameter is untrusted. Validate and canonicalise before use.
- A deep link must never perform a state-changing action without an
  authenticated session and, for destructive actions, a confirmation.
- Verify domain association files are correctly served, or links fall back to a
  scheme that any app can register and hijack.

### Network

- Certificate validation is never disabled. Not in debug, not behind a flag.
- Any URL derived from user input and then fetched by the backend is an SSRF
  risk. Enforce an allowlist of schemes, block private address ranges and cloud
  metadata endpoints, and do not follow redirects into them.

### Permissions and privacy

- Every requested permission maps to a shipped feature. Unused permissions are a
  finding, and a store-review risk.
- Privacy manifests and store data-disclosure forms must match what the code
  actually collects, including what third-party SDKs collect.
- Clipboard, screenshots, and background snapshots: verify sensitive screens are
  protected where the product requires it.

### Third-party SDKs

Each SDK is a party to your data. For every one: what does it collect, where
does it send it, and is that in the privacy documentation?

## Full MobSF — occasional, not CI

Run the full MobSF server as a **pre-release step**, not in the pipeline. Its
unique value is the third-party SDK inventory it extracts from the binary,
including detected versions — the closest thing available to a mobile SBOM.
Export it via the REST API and check the list against a CVE source and against
the privacy documentation.

**Known constraint:** MobSF has had structural trouble analysing binaries where
the JavaScript bundle runs inside a container application shipped as part of the
binary, which is how some managed React Native builds are packaged. Analysis may
hang. Verify on a current version before relying on it; if it fails, the SDK
inventory can be recovered from the dependency manifest plus the native build
output, and mobsfscan still covers source-level findings.

MobSF is GPL-3.0. Used as an external tool it imposes no obligation on your
code, but record it in the licence inventory.

## Release gate

Before any build reaches a store:

- [ ] No CRITICAL or HIGH open from any scanner
- [ ] All suppressions reviewed and still valid
- [ ] Permission list matches shipped features
- [ ] Privacy disclosures match actual collection, including SDKs
- [ ] No debug flags, test endpoints, or verbose logging in the release config
- [ ] Certificate validation enabled everywhere
- [ ] Deletion and export paths cover every data type added this cycle
