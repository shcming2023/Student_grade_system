/**
 * 学生成绩管理系统 JavaScript
 */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化确认删除对话框
    initDeleteConfirmations();
    
    // 初始化表单验证
    initFormValidation();
    
    // 初始化数据表格
    initDataTables();
});

// 确认删除功能
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.getAttribute('data-item-name') || '此项目';
            const deleteUrl = this.getAttribute('href');
            
            if (confirm(`确定要删除 "${itemName}" 吗？此操作不可撤销。`)) {
                window.location.href = deleteUrl;
            }
        });
    });
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// 数据表格初始化
function initDataTables() {
    // 如果页面有数据表格，添加排序功能
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this);
            });
        });
    });
}

// 表格排序功能
function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.classList.contains('sort-asc');
    
    // 移除所有排序类
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // 添加新的排序类
    header.classList.toggle(isAscending ? 'sort-desc' : 'sort-asc');
    
    // 排序行
    rows.sort((a, b) => {
        const aText = a.children[columnIndex].textContent.trim();
        const bText = b.children[columnIndex].textContent.trim();
        
        // 尝试数字比较
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // 字符串比较
        return isAscending ? 
            aText.localeCompare(bText, 'zh-CN') : 
            bText.localeCompare(aText, 'zh-CN');
    });
    
    // 重新排列行
    rows.forEach(row => tbody.appendChild(row));
}

// AJAX 请求封装
function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// 显示通知消息
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// 加载学生数据
function loadStudents() {
    apiRequest('/api/students')
        .then(data => {
            console.log('学生数据:', data);
            // 这里可以更新表格
        })
        .catch(error => {
            console.error('加载学生数据失败:', error);
            showNotification('加载学生数据失败', 'danger');
        });
}

// 加载成绩数据
function loadGrades() {
    apiRequest('/api/grades')
        .then(data => {
            console.log('成绩数据:', data);
            // 这里可以更新表格
        })
        .catch(error => {
            console.error('加载成绩数据失败:', error);
            showNotification('加载成绩数据失败', 'danger');
        });
}

// 添加学生
function addStudent(studentData) {
    apiRequest('/api/students', 'POST', studentData)
        .then(response => {
            if (response.success) {
                showNotification('学生添加成功', 'success');
                // 刷新页面或更新表格
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification('添加失败', 'danger');
            }
        })
        .catch(error => {
            console.error('添加学生失败:', error);
            showNotification('添加学生失败', 'danger');
        });
}

// 添加成绩
function addGrade(gradeData) {
    apiRequest('/api/grades', 'POST', gradeData)
        .then(response => {
            if (response.success) {
                showNotification('成绩添加成功', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification('添加失败', 'danger');
            }
        })
        .catch(error => {
            console.error('添加成绩失败:', error);
            showNotification('添加成绩失败', 'danger');
        });
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 格式化成绩等级
function formatGradeLevel(score) {
    if (score >= 90) return { text: '优秀', class: 'grade-excellent' };
    if (score >= 80) return { text: '良好', class: 'grade-good' };
    if (score >= 70) return { text: '中等', class: 'grade-average' };
    if (score >= 60) return { text: '及格', class: 'grade-pass' };
    return { text: '不及格', class: 'grade-fail' };
}

// 搜索功能
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.trim().toLowerCase();
    const rows = document.querySelectorAll('table tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// 导出数据
function exportData(type) {
    showNotification(`正在导出${type}数据...`, 'info');
    
    // 这里可以实现实际的导出逻辑
    setTimeout(() => {
        showNotification(`${type}数据导出成功`, 'success');
    }, 2000);
}

// 打印功能
function printTable() {
    window.print();
}

// 页面切换动画
function addPageTransition() {
    const main = document.querySelector('main');
    main.style.opacity = '0';
    
    setTimeout(() => {
        main.style.transition = 'opacity 0.3s ease';
        main.style.opacity = '1';
    }, 100);
}

// 初始化图表
function initCharts() {
    // 成绩分布饼图
    const gradeDistCtx = document.getElementById('gradeDistributionChart');
    if (gradeDistCtx) {
        apiRequest('/api/statistics')
            .then(data => {
                new Chart(gradeDistCtx, {
                    type: 'pie',
                    data: {
                        labels: data.grade_distribution.map(item => item.level),
                        datasets: [{
                            data: data.grade_distribution.map(item => item.count),
                            backgroundColor: [
                                '#28a745', '#17a2b8', '#ffc107', 
                                '#fd7e14', '#dc3545'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('加载统计数据失败:', error);
            });
    }
}

// 实用工具函数
const utils = {
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 节流函数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// 导出函数供全局使用
window.app = {
    loadStudents,
    loadGrades,
    addStudent,
    addGrade,
    showNotification,
    formatDate,
    formatGradeLevel,
    exportData,
    printTable,
    initCharts,
    utils
};