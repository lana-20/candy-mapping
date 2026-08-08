#!/usr/bin/env bash
# Resolves the vibium native binary, bypassing the Node.js `vibium` wrapper's
# startup cost -- a near-constant ~106-108ms per invocation, independent of the
# command (n=20 per cell; ~34% of a real 12-step journey, n=15). Measurements:
# the vibium-efficiency project, references/batched-cli-plan.md Measurement 5
# and references/cli-optimization-strategy.md technique 1.
#
# Usage: source this file, then use "$VIBIUM_NATIVE" wherever a script would
# otherwise call "vibium". Falls back to the "vibium" wrapper command itself
# if the native binary can't be resolved (e.g. non-global install, unsupported
# platform/arch), so callers stay correct even when the fast path isn't available.

resolve_vibium_native() {
  local bin
  bin=$(node -e "
    const path = require('path');
    const os = require('os');
    const platform = os.platform();
    const arch = os.arch() === 'x64' ? 'x64' : 'arm64';
    const pkg = \`@vibium/\${platform}-\${arch}\`;
    const binname = platform === 'win32' ? 'vibium.exe' : 'vibium';
    try {
      const p = require.resolve(\`\${pkg}/package.json\`, { paths: ['/usr/local/lib/node_modules/vibium'] });
      console.log(path.join(path.dirname(p), 'bin', binname));
    } catch (e) {
      process.exit(1);
    }
  " 2>/dev/null)
  if [ -n "$bin" ] && [ -x "$bin" ]; then
    echo "$bin"
  else
    echo "vibium"
  fi
}

VIBIUM_NATIVE="$(resolve_vibium_native)"
