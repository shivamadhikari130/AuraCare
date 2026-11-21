const path = require('path');
const fs = require('fs');

const BUBBLEWRAP_CORE = 'C:/Users/shiva/AppData/Local/npm-cache/_npx/881cef4662d2c421/node_modules/@bubblewrap/core';
const { TwaGenerator, TwaManifest, ConsoleLog } = require(BUBBLEWRAP_CORE);

async function run() {
  const targetDir = path.resolve('android_build');
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  if (fs.existsSync('android.keystore')) {
    fs.copyFileSync('android.keystore', path.join(targetDir, 'android.keystore'));
  }

  const manifestData = {
    packageId: "com.auracare.elderlycare",
    host: "localhost:8000",
    name: "AuraCare AI Elderly Care",
    launcherName: "AuraCare",
    display: "standalone",
    themeColor: "#059669",
    themeColorDark: "#047857",
    navigationColor: "#0f172a",
    navigationColorDark: "#020617",
    navigationDividerColor: "#00000000",
    navigationDividerColorDark: "#00000000",
    backgroundColor: "#0f172a",
    enableNotifications: true,
    startUrl: "/",
    iconUrl: "http://127.0.0.1:8000/static/icon-512.png",
    maskableIconUrl: "http://127.0.0.1:8000/static/icon-512.png",
    splashScreenFadeOutDuration: 300,
    signingKey: {
      path: path.join(targetDir, "android.keystore"),
      alias: "android"
    },
    appVersion: "1.0.0",
    appVersionCode: 1,
    shortcuts: [],
    generatorApp: "bubblewrap-cli",
    fallbackType: "webview",
    features: {},
    alphaDependencies: { enabled: false },
    enableSiteSettingsShortcut: true,
    isChromeOSOnly: false,
    isMetaQuest: false,
    minSdkVersion: 21,
    orientation: "portrait",
    fingerprints: [],
    additionalTrustedOrigins: []
  };

  const twaManifest = new TwaManifest(manifestData);
  await twaManifest.saveToFile(path.join(targetDir, "twa-manifest.json"));

  const log = new ConsoleLog('auracare_build');
  const generator = new TwaGenerator();
  console.log("Generating TWA Project in " + targetDir);
  await generator.createTwaProject(targetDir, twaManifest, log);
  console.log("TWA Project created successfully!");
}

run().catch(err => {
  console.error("Error creating TWA project:", err);
  process.exit(1);
});

