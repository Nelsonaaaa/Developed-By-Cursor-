// 获取DOM元素
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewArea = document.getElementById('previewArea');
const originalPreview = document.getElementById('originalPreview');
const compressedPreview = document.getElementById('compressedPreview');
const originalSize = document.getElementById('originalSize');
const compressedSize = document.getElementById('compressedSize');
const qualitySlider = document.getElementById('qualitySlider');
const qualityValue = document.getElementById('qualityValue');
const downloadBtn = document.getElementById('downloadBtn');

// 当前处理的图片数据
let currentFile = null;

// 绑定上传区域的点击事件
uploadArea.addEventListener('click', () => {
    imageInput.click();
});

// 处理拖拽上传
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#0071e3';
    uploadArea.style.backgroundColor = 'rgba(0, 113, 227, 0.05)';
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#d2d2d7';
    uploadArea.style.backgroundColor = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#d2d2d7';
    uploadArea.style.backgroundColor = 'transparent';
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleImageUpload(file);
    }
});

// 处理文件选择
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleImageUpload(file);
    }
});

// 处理图片上传
function handleImageUpload(file) {
    if (!file.type.startsWith('image/')) {
        alert('请上传图片文件！');
        return;
    }

    currentFile = file;
    
    // 显示原图大小
    originalSize.textContent = formatFileSize(file.size);
    
    // 预览原图
    const reader = new FileReader();
    reader.onload = (e) => {
        originalPreview.src = e.target.result;
        // 压缩图片
        compressImage(e.target.result, qualitySlider.value / 100);
    };
    reader.readAsDataURL(file);
    
    // 显示预览区域
    previewArea.style.display = 'block';
}

// 压缩图片
function compressImage(base64Str, quality) {
    // 如果质量设置为100%，直接使用原图
    if (quality >= 1) {
        compressedPreview.src = base64Str;
        // 使用原始文件大小
        document.getElementById('compressedSize').textContent = formatFileSize(currentFile.size);
        return;
    }

    const img = new Image();
    img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // 保持原始宽高比
        canvas.width = img.width;
        canvas.height = img.height;
        
        // 绘制图片
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        
        // 压缩图片
        const compressedBase64 = canvas.toDataURL(currentFile.type, quality);
        
        // 显示压缩后的图片
        compressedPreview.src = compressedBase64;
        
        // 计算压缩后的大小
        const compressedSize = Math.round((compressedBase64.length * 3) / 4);
        // 如果压缩后比原图还大，使用原图
        if (compressedSize > currentFile.size) {
            compressedPreview.src = base64Str;
            document.getElementById('compressedSize').textContent = formatFileSize(currentFile.size);
        } else {
            document.getElementById('compressedSize').textContent = formatFileSize(compressedSize);
        }
    };
    img.src = base64Str;
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 处理质量滑块变化
qualitySlider.addEventListener('input', (e) => {
    const quality = e.target.value;
    qualityValue.textContent = quality + '%';
    if (currentFile) {
        const reader = new FileReader();
        reader.onload = (e) => {
            compressImage(e.target.result, quality / 100);
        };
        reader.readAsDataURL(currentFile);
    }
});

// 处理下载按钮点击
downloadBtn.addEventListener('click', () => {
    if (!compressedPreview.src) return;
    
    const link = document.createElement('a');
    link.download = 'compressed_' + currentFile.name;
    link.href = compressedPreview.src;
    link.click();
}); 