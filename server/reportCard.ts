import puppeteer from "puppeteer";

/**
 * 成绩单数据接口
 */
export interface ReportCardData {
  // 学生信息
  studentName: string;
  studentNumber: string;
  schoolName: string;
  grade: string;
  className: string;
  
  // 考试信息
  examName: string;
  schoolYear: string;
  semester: string;
  examDate: string;
  
  // 成绩数据
  subjects: Array<{
    name: string;
    score: number;
    totalScore: number;
  }>;
  
  // 统计信息
  totalScore: number;
  totalPossibleScore: number;
  averageScore: number;
  classRank?: number;
  classTotal?: number;
  
  // 评语
  teacherComment?: string;
}

/**
 * 生成成绩单HTML
 */
function generateReportCardHTML(data: ReportCardData): string {
  const { subjects, totalScore, totalPossibleScore, averageScore } = data;
  
  // 计算百分比用于图表
  const subjectPercentages = subjects.map(s => ({
    name: s.name,
    percentage: (s.score / s.totalScore) * 100
  }));
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    @page {
      size: A4;
      margin: 0;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: "SimSun", "STSong", serif;
      font-size: 12pt;
      line-height: 1.5;
    }
    
    /* 第一页样式 */
    .page {
      width: 210mm;
      height: 297mm;
      padding: 20mm;
      page-break-after: always;
      position: relative;
    }
    
    .header {
      text-align: center;
      margin-bottom: 15mm;
      border-bottom: 2px solid #333;
      padding-bottom: 5mm;
    }
    
    .header h1 {
      font-size: 24pt;
      font-weight: bold;
      margin-bottom: 3mm;
    }
    
    .header .school-name {
      font-size: 14pt;
      color: #666;
    }
    
    .info-section {
      margin-bottom: 8mm;
    }
    
    .info-row {
      display: flex;
      margin-bottom: 3mm;
      font-size: 11pt;
    }
    
    .info-label {
      font-weight: bold;
      width: 80px;
    }
    
    .info-value {
      flex: 1;
    }
    
    .section-title {
      font-size: 14pt;
      font-weight: bold;
      margin: 8mm 0 4mm 0;
      padding-bottom: 2mm;
      border-bottom: 1px solid #999;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 5mm;
    }
    
    th, td {
      border: 1px solid #333;
      padding: 3mm 2mm;
      text-align: center;
    }
    
    th {
      background-color: #f0f0f0;
      font-weight: bold;
    }
    
    .score-cell {
      font-size: 13pt;
      font-weight: bold;
    }
    
    /* 第二页样式 */
    .statistics {
      margin-bottom: 8mm;
    }
    
    .stat-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4mm;
      margin-bottom: 5mm;
    }
    
    .stat-box {
      border: 2px solid #333;
      padding: 4mm;
      text-align: center;
    }
    
    .stat-label {
      font-size: 10pt;
      color: #666;
      margin-bottom: 2mm;
    }
    
    .stat-value {
      font-size: 20pt;
      font-weight: bold;
      color: #333;
    }
    
    .chart-container {
      margin: 8mm 0;
      padding: 5mm;
      border: 1px solid #ddd;
      background-color: #f9f9f9;
    }
    
    .bar-chart {
      margin-top: 4mm;
    }
    
    .bar-item {
      display: flex;
      align-items: center;
      margin-bottom: 3mm;
    }
    
    .bar-label {
      width: 60px;
      font-size: 10pt;
    }
    
    .bar-container {
      flex: 1;
      height: 20px;
      background-color: #e0e0e0;
      border-radius: 3px;
      overflow: hidden;
      margin: 0 3mm;
    }
    
    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #4CAF50, #8BC34A);
      transition: width 0.3s ease;
    }
    
    .bar-value {
      width: 50px;
      text-align: right;
      font-size: 10pt;
      font-weight: bold;
    }
    
    .comment-section {
      margin-top: 8mm;
      border: 1px solid #333;
      padding: 5mm;
      min-height: 40mm;
    }
    
    .comment-title {
      font-weight: bold;
      margin-bottom: 3mm;
    }
    
    .comment-content {
      line-height: 1.8;
      min-height: 30mm;
    }
    
    .signature-section {
      margin-top: 10mm;
      display: flex;
      justify-content: space-between;
    }
    
    .signature-box {
      width: 45%;
      border: 1px solid #333;
      padding: 5mm;
      min-height: 25mm;
    }
    
    .signature-label {
      font-weight: bold;
      margin-bottom: 8mm;
    }
    
    .signature-line {
      border-bottom: 1px solid #333;
      margin-top: 10mm;
    }
  </style>
</head>
<body>
  <!-- 第一页：学生信息和成绩表 -->
  <div class="page">
    <div class="header">
      <h1>学生成绩单</h1>
      <div class="school-name">${data.schoolName}</div>
    </div>
    
    <div class="info-section">
      <div class="info-row">
        <span class="info-label">姓名：</span>
        <span class="info-value">${data.studentName}</span>
        <span class="info-label">学号：</span>
        <span class="info-value">${data.studentNumber}</span>
      </div>
      <div class="info-row">
        <span class="info-label">年级：</span>
        <span class="info-value">${data.grade}</span>
        <span class="info-label">班级：</span>
        <span class="info-value">${data.className}</span>
      </div>
    </div>
    
    <div class="info-section">
      <div class="info-row">
        <span class="info-label">考试名称：</span>
        <span class="info-value">${data.examName}</span>
      </div>
      <div class="info-row">
        <span class="info-label">学年学期：</span>
        <span class="info-value">${data.schoolYear} ${data.semester}</span>
        <span class="info-label">考试日期：</span>
        <span class="info-value">${data.examDate}</span>
      </div>
    </div>
    
    <div class="section-title">各科成绩</div>
    <table>
      <thead>
        <tr>
          <th style="width: 50px;">序号</th>
          <th>科目</th>
          <th style="width: 100px;">得分</th>
          <th style="width: 100px;">满分</th>
          <th style="width: 100px;">得分率</th>
        </tr>
      </thead>
      <tbody>
        ${subjects.map((subject, index) => `
          <tr>
            <td>${index + 1}</td>
            <td>${subject.name}</td>
            <td class="score-cell">${subject.score.toFixed(1)}</td>
            <td>${subject.totalScore.toFixed(1)}</td>
            <td>${((subject.score / subject.totalScore) * 100).toFixed(1)}%</td>
          </tr>
        `).join('')}
        <tr style="font-weight: bold; background-color: #f0f0f0;">
          <td colspan="2">总计</td>
          <td class="score-cell">${totalScore.toFixed(1)}</td>
          <td>${totalPossibleScore.toFixed(1)}</td>
          <td>${((totalScore / totalPossibleScore) * 100).toFixed(1)}%</td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <!-- 第二页：成绩统计和评语 -->
  <div class="page">
    <div class="section-title">成绩统计</div>
    <div class="stat-grid">
      <div class="stat-box">
        <div class="stat-label">总分</div>
        <div class="stat-value">${totalScore.toFixed(1)}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">平均分</div>
        <div class="stat-value">${averageScore.toFixed(1)}</div>
      </div>
      ${data.classRank && data.classTotal ? `
      <div class="stat-box">
        <div class="stat-label">班级排名</div>
        <div class="stat-value">${data.classRank}/${data.classTotal}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">得分率</div>
        <div class="stat-value">${((totalScore / totalPossibleScore) * 100).toFixed(1)}%</div>
      </div>
      ` : ''}
    </div>
    
    <div class="section-title">各科成绩分析</div>
    <div class="chart-container">
      <div class="bar-chart">
        ${subjectPercentages.map(item => `
          <div class="bar-item">
            <div class="bar-label">${item.name}</div>
            <div class="bar-container">
              <div class="bar-fill" style="width: ${item.percentage}%"></div>
            </div>
            <div class="bar-value">${item.percentage.toFixed(1)}%</div>
          </div>
        `).join('')}
      </div>
    </div>
    
    <div class="comment-section">
      <div class="comment-title">教师评语</div>
      <div class="comment-content">
        ${data.teacherComment || '（暂无评语）'}
      </div>
    </div>
    
    <div class="signature-section">
      <div class="signature-box">
        <div class="signature-label">教师签名：</div>
        <div class="signature-line"></div>
      </div>
      <div class="signature-box">
        <div class="signature-label">家长签名：</div>
        <div class="signature-line"></div>
      </div>
    </div>
  </div>
</body>
</html>
  `;
}

/**
 * 生成成绩单PDF
 * @param data 成绩单数据
 * @returns PDF Buffer
 */
export async function generateReportCardPDF(data: ReportCardData): Promise<Buffer> {
  const html = generateReportCardHTML(data);
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });
    
    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      }
    });
    
    return Buffer.from(pdfBuffer);
  } finally {
    await browser.close();
  }
}
