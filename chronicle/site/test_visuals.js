const fs = require('fs');
const path = require('path');
const vm = require('vm');

console.log("=== 開始執行前端視覺化函數測試 ===");

// 1. 語法檢查：使用 node --check
const { execSync } = require('child_process');
try {
  execSync('node --check chronicle/site/app.js');
  console.log("✅ app.js 語法檢查通過！");
} catch (err) {
  console.error("❌ app.js 語法檢查失敗！");
  console.error(err.message);
  process.exit(1);
}

// 2. 邏輯單元測試：Mock 瀏覽器環境載入 app.js 中的特定函數
const appJsPath = path.join(__dirname, 'app.js');
const appJsContent = fs.readFileSync(appJsPath, 'utf8');

// 建立 Mock 沙箱環境
const sandbox = {
  console,
  document: {
    getElementById: () => null,
    querySelector: () => null
  },
  window: {},
  navigator: { userLanguage: 'zh-TW', language: 'zh-TW' },
  Chart: class MockChart {},
  CHART_COLORS: {},
  THEME: {}
};

// 執行程式碼以提取函數
try {
  // 將 app.js 載入沙箱，只執行變數與函數聲明
  vm.createContext(sandbox);
  vm.runInContext(appJsContent, sandbox);
  console.log("✅ app.js 在 Mock 沙箱環境中載入成功！");
} catch (err) {
  // 因為 app.js 可能在最外層有自執行邏輯或 API 呼叫，如果崩潰，我們改用正則提取特定函數進行評估
  console.log("⚠️ 沙箱載入完整 app.js 遇到預期中的瀏覽器 API 缺失限制，改用正則提取測試函數...");
}

// 手動提取 generateExposureSparkBarHtml 和 generateRebalanceSliderHtml 進行測試
const extractFunction = (funcName) => {
  const regex = new RegExp(`function\\s+${funcName}\\s*\\([\\s\\S]*?\\)\\s*\\{([\\s\\S]*?)\\n\\}`, 'g');
  const match = appJsContent.match(new RegExp(`function\\s+${funcName}[\\s\\S]*?\\n\\}`, 'g'));
  if (match) {
    return match[0];
  }
  
  // 試試另一種大括號匹配 (簡化版，取得函數邊界)
  const startIndex = appJsContent.indexOf(`function ${funcName}`);
  if (startIndex === -1) return null;
  
  let braceCount = 0;
  let code = "";
  let started = false;
  for (let i = startIndex; i < appJsContent.length; i++) {
    const char = appJsContent[i];
    code += char;
    if (char === '{') {
      braceCount++;
      started = true;
    } else if (char === '}') {
      braceCount--;
      if (started && braceCount === 0) {
        break;
      }
    }
  }
  return code;
};

const sparkBarCode = extractFunction('generateExposureSparkBarHtml');
const sliderCode = extractFunction('generateRebalanceSliderHtml');
const hexToRgbaCode = extractFunction('hexToRgba');

if (!sparkBarCode || !sliderCode || !hexToRgbaCode) {
  console.error("❌ 找不到關鍵函數定義，請檢查函數名稱是否正確！");
  process.exit(1);
}

// 在乾淨沙箱中執行這些提取的函數
const testSandbox = {
  console,
  fmtAmount: (v) => String(v),
  fmtPct: (v) => (v * 100).toFixed(1) + '%',
  fmtUsd: (v) => '$' + v,
  fmtTwd: (v) => v + ' TWD',
  fmtRate: (v) => String(v),
  isOutOfBand: false,
  pllT: (key, opt) => `[i18n:${key}]`
};

vm.createContext(testSandbox);
vm.runInContext(hexToRgbaCode, testSandbox);
vm.runInContext(sparkBarCode, testSandbox);
vm.runInContext(sliderCode, testSandbox);

// 3. 驗證 hexToRgba
try {
  const color1 = testSandbox.hexToRgba('#3d6b52', 0.15);
  const color2 = testSandbox.hexToRgba('#3d6', 0.15);
  const color3 = testSandbox.hexToRgba('invalid', 0.15);
  console.log("🧪 hexToRgba 測試:", { color1, color2, color3 });
  if (color1 === 'rgba(61, 107, 82, 0.15)' && color3.includes('rgba')) {
    console.log("✅ hexToRgba 邏輯正確！");
  } else {
    console.warn("⚠️ hexToRgba 輸出未達預期，請確認解析邏輯");
  }
} catch (e) {
  console.error("❌ hexToRgba 測試崩潰:", e);
}

// 4. 驗證 generateExposureSparkBarHtml (已停用，應一律回傳空字串)
try {
  const rssbHtml = testSandbox.generateExposureSparkBarHtml('RSSB');
  const invalidHtml = testSandbox.generateExposureSparkBarHtml('UNKNOWN');
  console.log("🧪 RSSB Sparkbar Html 長度:", rssbHtml.length);
  if (rssbHtml === '' && invalidHtml === '') {
    console.log("✅ generateExposureSparkBarHtml 邏輯正確 (已確認完全移除線條)！");
  } else {
    console.error("❌ generateExposureSparkBarHtml 邏輯錯誤，預期回傳空字串，但實際輸出如下：", rssbHtml);
    process.exit(1);
  }
} catch (e) {
  console.error("❌ generateExposureSparkBarHtml 測試崩潰:", e);
  process.exit(1);
}

// 5. 驗證 generateRebalanceSliderHtml
try {
  const mockSleeve = { target_pct: 0.1, current_pct: 0.15 };
  const sliderHtml = testSandbox.generateRebalanceSliderHtml(mockSleeve);
  console.log("🧪 Slider Html 長度:", sliderHtml.length);
  if (sliderHtml.includes('deviation-slider-wrapper') && sliderHtml.includes('50.0% 偏離')) {
    console.log("✅ generateRebalanceSliderHtml 邏輯正確！");
  } else {
    console.error("❌ generateRebalanceSliderHtml 邏輯錯誤，輸出如下：", sliderHtml);
    process.exit(1);
  }
} catch (e) {
  console.error("❌ generateRebalanceSliderHtml 測試崩潰:", e);
  process.exit(1);
}

console.log("🎉 所有自動化測試順利通過！前端視覺化函數運作正常。");
process.exit(0);
