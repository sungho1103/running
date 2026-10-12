// API 기본 URL
const API_BASE = '';

// 차트 인스턴스
let distanceChart = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 오늘 날짜 자동 설정
    document.getElementById('date').valueAsDate = new Date();

    // 폼 이벤트 리스너
    document.getElementById('record-form').addEventListener('submit', handleRecordSubmit);
    document.getElementById('analysis-form').addEventListener('submit', handleAnalysisSubmit);
    document.getElementById('image').addEventListener('change', handleImagePreview);

    // 초기 데이터 로드
    loadStats();
    loadRecords();
    initChart();
});

// 토스트 알림 표시
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // 3초 후 자동 제거
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 차트 초기화
function initChart() {
    const ctx = document.getElementById('distanceChart');
    if (!ctx) return;

    distanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '거리 (km)',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: '주간 거리 추이'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '거리 (km)'
                    }
                }
            }
        }
    });
}

// 차트 업데이트
function updateChart(records) {
    if (!distanceChart || !records || records.length === 0) return;

    // 최근 7개 기록만 표시
    const recentRecords = records.slice(0, 7).reverse();
    const labels = recentRecords.map(r => r.date);
    const data = recentRecords.map(r => r.distance || 0);

    distanceChart.data.labels = labels;
    distanceChart.data.datasets[0].data = data;
    distanceChart.update();
}

// 탭 전환
function showTab(tabName) {
    // 모든 탭 콘텐츠 숨기기
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 선택된 탭 활성화
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');

    // 히스토리 탭 선택 시 데이터 로드
    if (tabName === 'history') {
        loadRecords();
        loadAnalyses();
    }
}

// 운동 기록 제출
async function handleRecordSubmit(e) {
    e.preventDefault();

    const data = {
        date: document.getElementById('date').value,
        distance: parseFloat(document.getElementById('distance').value) || null,
        duration: parseInt(document.getElementById('duration').value) || null,
        pace: document.getElementById('pace').value || null,
        notes: document.getElementById('notes').value || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/records`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('저장 실패');

        showToast('운동 기록이 저장되었습니다!', 'success');
        e.target.reset();
        document.getElementById('date').valueAsDate = new Date();
        loadStats();
        loadRecords();
    } catch (error) {
        showToast(`오류: ${error.message}`, 'error');
    }
}

// AI 분석 제출
async function handleAnalysisSubmit(e) {
    e.preventDefault();

    const imageInput = document.getElementById('image');
    const file = imageInput.files[0];

    if (!file) {
        showToast('이미지를 선택해주세요', 'error');
        return;
    }

    // 파일 크기 검증 (2MB)
    if (file.size > 2 * 1024 * 1024) {
        showToast('파일 크기는 2MB 이하여야 합니다', 'error');
        return;
    }

    // 로딩 상태
    const btnText = document.getElementById('analyze-btn-text');
    const loading = document.getElementById('analyze-loading');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    btnText.style.display = 'none';
    loading.style.display = 'inline-block';
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch(`${API_BASE}/api/analyses`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '분석 실패');
        }

        const result = await response.json();

        // 결과 표시
        document.getElementById('analysis-result').style.display = 'block';
        document.getElementById('analysis-content').textContent = result.analysis_result;
        document.getElementById('tokens-used').textContent = result.tokens_used || 0;
        document.getElementById('cost').textContent = `$${(result.cost || 0).toFixed(4)}`;

        showToast('AI 분석이 완료되었습니다!', 'success');

        // 스크롤 이동
        document.getElementById('analysis-result').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showToast(`분석 오류: ${error.message}`, 'error');
    } finally {
        // 로딩 상태 해제
        btnText.style.display = 'inline-block';
        loading.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// 이미지 미리보기
function handleImagePreview(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('image-preview');

    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" alt="미리보기">`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
}

// 통계 로드
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/records/stats`);
        const stats = await response.json();

        document.getElementById('total-records').textContent = stats.total_records;
        document.getElementById('total-distance').textContent = `${stats.total_distance.toFixed(1)} km`;
        document.getElementById('total-duration').textContent = `${stats.total_duration} 분`;
    } catch (error) {
        console.error('통계 로드 실패:', error);
    }
}

// 운동 기록 리스트 로드
async function loadRecords() {
    try {
        const response = await fetch(`${API_BASE}/api/records`);
        const records = await response.json();

        const listContainer = document.getElementById('records-list');

        if (records.length === 0) {
            listContainer.innerHTML = '<p class="empty-state">아직 기록이 없습니다</p>';
            return;
        }

        listContainer.innerHTML = records.map(record => `
            <div class="record-item">
                <h3>${record.date}</h3>
                ${record.distance ? `<p>거리: ${record.distance} km</p>` : ''}
                ${record.duration ? `<p>시간: ${record.duration} 분</p>` : ''}
                ${record.pace ? `<p>페이스: ${record.pace}</p>` : ''}
                ${record.notes ? `<p>메모: ${record.notes}</p>` : ''}
            </div>
        `).join('');

        // 차트 업데이트
        updateChart(records);
    } catch (error) {
        console.error('기록 로드 실패:', error);
    }
}

// AI 분석 히스토리 로드
async function loadAnalyses() {
    try {
        const response = await fetch(`${API_BASE}/api/analyses`);
        const analyses = await response.json();

        const listContainer = document.getElementById('analyses-list');

        if (analyses.length === 0) {
            listContainer.innerHTML = '<p class="empty-state">아직 분석 기록이 없습니다</p>';
            return;
        }

        listContainer.innerHTML = analyses.map(analysis => {
            const date = new Date(analysis.created_at).toLocaleString('ko-KR');
            return `
                <div class="analysis-item">
                    <h3>${date}</h3>
                    <p>토큰: ${analysis.tokens_used} | 비용: $${(analysis.cost || 0).toFixed(4)}</p>
                    <p style="white-space: pre-wrap; margin-top: 10px;">${analysis.analysis_result}</p>
                    ${analysis.image_path ? `<img src="/${analysis.image_path}" style="max-width: 100%; margin-top: 10px; border-radius: 6px;">` : ''}
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('분석 이력 로드 실패:', error);
    }
}
