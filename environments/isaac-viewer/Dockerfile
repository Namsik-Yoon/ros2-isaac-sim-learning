# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
# Adapted from Isaac Sim v6.2.0's official WebRTC viewer:
# https://github.com/isaac-sim/IsaacSim/blob/v6.2.0/tools/docker/web-viewer/Dockerfile
# Changes: Node 22 base, reuse built dependencies, explicit HTTP bind at runtime,
# and a Web Crypto UUID fallback for trusted-LAN HTTP viewers.
# The generated NVIDIA Web SDK application retains its own package licenses.

FROM node:22-bookworm-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN printf '%s\n' '@nvidia:registry=https://edge.urm.nvidia.com/artifactory/api/npm/omniverse-client-npm/' > /root/.npmrc \
    && npx --yes @nvidia/create-ov-web-rtc-app@2.1.5 --name=web-viewer --sample=local-sample --external --outputDir=/app sample-app --framework=react \
    && rm -f /root/.npmrc

WORKDIR /app/web-viewer
ARG ISAACSIM_HOST=127.0.0.1
ARG ISAACSIM_SIGNAL_PORT=49100
ARG ISAACSIM_STREAM_PORT=47998

# These values are compiled into the browser client. Rebuild when they change.
RUN node -e 'const e = process.env; if (!/^[A-Za-z0-9.:-]+$/.test(e.ISAACSIM_HOST)) throw new Error("Invalid ISAACSIM_HOST"); for (const k of ["ISAACSIM_SIGNAL_PORT", "ISAACSIM_STREAM_PORT"]) { const p = Number(e[k]); if (!/^\d+$/.test(e[k]) || !Number.isInteger(p) || p < 1 || p > 65535) throw new Error("Invalid " + k); }' \
    && grep -qF "signalingServer: '127.0.0.1'," src/main.tsx \
    && sed -i "s/signalingServer: [^,]*/signalingServer: '${ISAACSIM_HOST}'/" src/main.tsx \
    && sed -i "/signalingServer:/a\\    signalingPort: ${ISAACSIM_SIGNAL_PORT},\n    mediaServer: '${ISAACSIM_HOST}',\n    mediaPort: ${ISAACSIM_STREAM_PORT},\n    forceWSS: false," src/main.tsx \
    && grep -qF "signalingPort: ${ISAACSIM_SIGNAL_PORT}," src/main.tsx \
    && grep -qF "mediaPort: ${ISAACSIM_STREAM_PORT}," src/main.tsx

# randomUUID requires a secure context; getRandomValues remains available on HTTP.
# Preserve native randomUUID and use the standard UUID v4 algorithm when absent.
# https://www.w3.org/TR/webcrypto-2/#Crypto-method-randomUUID
RUN grep -qF 'void app.initialize();' src/main.tsx \
    && sed -i '/void app.initialize/i\
if (typeof globalThis.crypto.randomUUID !== "function") {\
    Object.defineProperty(globalThis.crypto, "randomUUID", {\
        configurable: true,\
        value: () => {\
            const bytes = globalThis.crypto.getRandomValues(new Uint8Array(16));\
            const view = new DataView(bytes.buffer);\
            view.setUint8(6, (view.getUint8(6) & 0x0f) | 0x40);\
            view.setUint8(8, (view.getUint8(8) & 0x3f) | 0x80);\
            const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");\
            return [hex.slice(0, 8), hex.slice(8, 12), hex.slice(12, 16), hex.slice(16, 20), hex.slice(20)].join("-");\
        },\
    });\
}' src/main.tsx \
    && grep -qF 'Object.defineProperty(globalThis.crypto, "randomUUID"' src/main.tsx

# Preserve browser shortcuts while forwarding normal input to Isaac Sim.
# F7 still reaches Isaac Sim, but must not trigger Chrome's caret-browsing UI.
# Clipboard shortcuts remain under the WebRTC client's control.
RUN grep -qF 'void app.initialize();' src/main.tsx \
    && sed -i '/void app.initialize/i\
const sc = document.getElementById("stream-container");\
if (sc) {\
    sc.addEventListener("keydown", (e: KeyboardEvent) => {\
        if (e.key === "F11" || e.code === "F11") { e.preventDefault(); e.stopPropagation(); if (document.fullscreenElement) { document.exitFullscreen(); } else { document.documentElement.requestFullscreen(); } return; }\
        if (e.key === "F7") { e.preventDefault(); return; }\
        if (e.key === "F5" || e.code === "F5") { e.preventDefault(); e.stopPropagation(); window.location.reload(); return; }\
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "r") { e.preventDefault(); e.stopPropagation(); window.location.reload(); return; }\
        if (e.key === "F12" || e.code === "F12") { e.stopPropagation(); return; }\
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && ["i","j","c"].includes(e.key.toLowerCase())) { e.stopPropagation(); return; }\
        if (e.metaKey && e.altKey && ["i","j","c"].includes(e.key.toLowerCase())) { e.stopPropagation(); return; }\
    }, true);\
}' src/main.tsx \
    && grep -qF 'const sc = document.getElementById("stream-container");' src/main.tsx

# Pin the SDK version verified with this viewer; the generator defaults to 6.x.
RUN node -e 'const fs = require("node:fs"); const path = "package.json"; const pkg = JSON.parse(fs.readFileSync(path, "utf8")); pkg.dependencies["@nvidia/ov-web-rtc"] = "6.8.2"; fs.writeFileSync(path, JSON.stringify(pkg, null, 2) + "\n");' \
    && npm install --ignore-scripts \
    && npm run build

FROM node:22-bookworm-slim
RUN groupadd --gid 1234 appuser \
    && useradd --no-log-init --uid 1234 --gid appuser --create-home --home-dir /app --shell /usr/sbin/nologin appuser

WORKDIR /app
COPY --from=builder --chown=1234:1234 /app/web-viewer/package.json /app/web-viewer/package-lock.json ./
COPY --from=builder --chown=1234:1234 /app/web-viewer/node_modules ./node_modules
COPY --from=builder --chown=1234:1234 /app/web-viewer/dist ./dist

USER appuser
EXPOSE 8210
ENTRYPOINT ["/app/node_modules/.bin/vite", "preview", "--strictPort"]
CMD ["--host", "127.0.0.1", "--port", "8210"]
