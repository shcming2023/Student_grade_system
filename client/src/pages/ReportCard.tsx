import { useRoute } from "wouter";
import { trpc } from "@/lib/trpc";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, Download, Printer } from "lucide-react";
import { Link } from "wouter";
import { useRef, useState } from "react";
import { toast } from "sonner";

export default function ReportCard() {
  const [, params] = useRoute("/report-card/:examId/:studentId");
  const examId = params?.examId ? parseInt(params.examId) : null;
  const studentId = params?.studentId ? parseInt(params.studentId) : null;
  
  const printRef = useRef<HTMLDivElement>(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  const { data: reportData, isLoading } = trpc.reportCard.getReportCard.useQuery(
    { examId: examId!, studentId: studentId! },
    { enabled: !!examId && !!studentId }
  );
  
  const generatePDFMutation = trpc.reportCard.generatePDF.useMutation();

  const handlePrint = () => {
    if (printRef.current) {
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>成绩单 - ${reportData?.studentInfo.studentName}</title>
              <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                  font-family: 'Microsoft YaHei', Arial, sans-serif; 
                  padding: 40px; 
                  background: white;
                  font-size: 14px;
                  line-height: 1.6;
                }
                .report-card { max-width: 900px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; border-bottom: 3px solid #2563eb; padding-bottom: 20px; }
                .header h1 { font-size: 32px; color: #1e40af; margin-bottom: 10px; }
                .header .subtitle { font-size: 16px; color: #64748b; }
                .section { margin-bottom: 30px; page-break-inside: avoid; }
                .section-title { 
                  font-size: 20px; 
                  font-weight: bold; 
                  color: #1e40af; 
                  margin-bottom: 15px; 
                  padding-bottom: 8px;
                  border-bottom: 2px solid #e2e8f0;
                }
                .info-grid { 
                  display: grid; 
                  grid-template-columns: repeat(2, 1fr); 
                  gap: 15px; 
                  margin-bottom: 20px; 
                }
                .info-item { 
                  padding: 12px; 
                  background: #f8fafc; 
                  border-radius: 6px;
                  border-left: 3px solid #3b82f6;
                }
                .info-label { font-weight: 600; color: #475569; margin-bottom: 4px; }
                .info-value { font-size: 16px; color: #0f172a; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { padding: 12px; text-align: left; border: 1px solid #e2e8f0; }
                th { background: #f1f5f9; font-weight: 600; color: #334155; }
                tr:nth-child(even) { background: #f8fafc; }
                .score-cell { text-align: center; font-weight: 600; }
                .total-row { background: #dbeafe !important; font-weight: bold; }
                .analysis-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
                .analysis-item { 
                  padding: 15px; 
                  background: #f8fafc; 
                  border-radius: 8px; 
                  border: 1px solid #e2e8f0;
                }
                .analysis-header { 
                  font-weight: 600; 
                  color: #1e40af; 
                  margin-bottom: 8px; 
                  font-size: 15px;
                }
                .analysis-stats { display: flex; justify-content: space-between; margin-bottom: 6px; }
                .percentage { 
                  font-size: 20px; 
                  font-weight: bold; 
                  color: #2563eb; 
                  margin-top: 8px;
                }
                .percentage.good { color: #16a34a; }
                .percentage.medium { color: #ea580c; }
                .percentage.poor { color: #dc2626; }
                .comment-box { 
                  border: 2px dashed #cbd5e1; 
                  border-radius: 8px; 
                  padding: 20px; 
                  min-height: 150px; 
                  background: #fafafa;
                }
                .comment-label { 
                  font-weight: 600; 
                  color: #475569; 
                  margin-bottom: 10px; 
                }
                @media print {
                  body { padding: 20px; }
                  .no-print { display: none; }
                  @page { margin: 1.5cm; }
                }
              </style>
            </head>
            <body>
              ${printRef.current.innerHTML}
            </body>
          </html>
        `);
        printWindow.document.close();
        setTimeout(() => {
          printWindow.print();
          printWindow.close();
        }, 250);
      }
    }
  };

  const handleDownloadPDF = async () => {
    if (!examId || !studentId) {
      toast.error('缺少必要参数');
      return;
    }
    
    setIsGeneratingPDF(true);
    try {
      const result = await generatePDFMutation.mutateAsync({
        examId,
        studentId,
        schoolName: 'Way To Future',
      });
      
      // 将base64转换为BlobURL
      const byteCharacters = atob(result.pdf);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      
      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast.success('成绩单PDF导出成功');
    } catch (error) {
      console.error('PDF生成失败:', error);
      toast.error('成绩单PDF生成失败，请稍后重试');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </DashboardLayout>
    );
  }

  if (!reportData) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <p>成绩单数据不存在</p>
                <Link href="/scores">
                  <Button variant="link" className="mt-4">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    返回成绩查询
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  const getPercentageClass = (percentage: number) => {
    if (percentage >= 80) return "good";
    if (percentage >= 60) return "medium";
    return "poor";
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* 操作按钮 */}
        <div className="flex items-center justify-between no-print">
          <Link href="/scores">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              返回
            </Button>
          </Link>
          <div className="flex gap-2">
            <Button onClick={handlePrint} variant="outline">
              <Printer className="mr-2 h-4 w-4" />
              打印成绩单
            </Button>
            <Button 
              onClick={handleDownloadPDF} 
              disabled={isGeneratingPDF}
            >
              {isGeneratingPDF ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  导出PDF
                </>
              )}
            </Button>
          </div>
        </div>

        {/* 成绩单内容 */}
        <div ref={printRef} className="report-card">
          {/* 标题 */}
          <div className="header">
            <h1>学生成绩单</h1>
            <div className="subtitle">{reportData.examInfo.examName}</div>
          </div>

          {/* 第一部分：基本信息 */}
          <div className="section">
            <div className="section-title">一、基本信息</div>
            <div className="info-grid">
              <div className="info-item">
                <div className="info-label">学生姓名</div>
                <div className="info-value">{reportData.studentInfo.studentName}</div>
              </div>
              <div className="info-item">
                <div className="info-label">学号</div>
                <div className="info-value">{reportData.studentInfo.studentNumber}</div>
              </div>
              <div className="info-item">
                <div className="info-label">班级</div>
                <div className="info-value">{reportData.studentInfo.className}</div>
              </div>
              <div className="info-item">
                <div className="info-label">年级</div>
                <div className="info-value">{reportData.examInfo.gradeName}</div>
              </div>
              <div className="info-item">
                <div className="info-label">科目</div>
                <div className="info-value">{reportData.examInfo.subjectName}</div>
              </div>
              <div className="info-item">
                <div className="info-label">考试日期</div>
                <div className="info-value">
                  {new Date(reportData.examInfo.examDate).toLocaleDateString('zh-CN')}
                </div>
              </div>
            </div>
            <div className="info-grid">
              <div className="info-item" style={{ gridColumn: 'span 2' }}>
                <div className="info-label">总分</div>
                <div className="info-value" style={{ fontSize: '24px', color: '#2563eb', fontWeight: 'bold' }}>
                  {reportData.totalEarned} / {reportData.totalMax} 分 
                  <span style={{ marginLeft: '20px', fontSize: '20px', color: '#16a34a' }}>
                    （{reportData.percentage}%）
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 第二部分：成绩得分清单 */}
          <div className="section">
            <div className="section-title">二、成绩得分清单</div>
            <table>
              <thead>
                <tr>
                  <th style={{ width: '80px' }}>题号</th>
                  <th>模块</th>
                  <th>知识点</th>
                  <th style={{ width: '120px' }}>题型</th>
                  <th style={{ width: '100px', textAlign: 'center' }}>满分</th>
                  <th style={{ width: '100px', textAlign: 'center' }}>得分</th>
                </tr>
              </thead>
              <tbody>
                {reportData.questionScores.map((q, idx) => (
                  <tr key={idx}>
                    <td className="score-cell">第{q.questionNumber}题</td>
                    <td>{q.module || '-'}</td>
                    <td>{q.knowledgePoint || '-'}</td>
                    <td>{q.questionType || '-'}</td>
                    <td className="score-cell">{q.maxScore}</td>
                    <td className="score-cell" style={{ 
                      color: q.studentScore === q.maxScore ? '#16a34a' : '#dc2626',
                      fontWeight: 'bold'
                    }}>
                      {q.studentScore}
                    </td>
                  </tr>
                ))}
                <tr className="total-row">
                  <td colSpan={4} style={{ textAlign: 'right', fontWeight: 'bold' }}>总计</td>
                  <td className="score-cell">{reportData.totalMax}</td>
                  <td className="score-cell">{reportData.totalEarned}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* 第三部分：成绩分析 */}
          <div className="section">
            <div className="section-title">三、成绩分析</div>
            
            {/* 按模块分析 */}
            <div style={{ marginBottom: '25px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#334155', marginBottom: '12px' }}>
                （一）按模块统计
              </h3>
              <div className="analysis-grid">
                {reportData.moduleAnalysis.map((m, idx) => (
                  <div key={idx} className="analysis-item">
                    <div className="analysis-header">{m.module}</div>
                    <div className="analysis-stats">
                      <span>题目数量：{m.count}题</span>
                    </div>
                    <div className="analysis-stats">
                      <span>得分：{m.earned} / {m.max}</span>
                    </div>
                    <div className={`percentage ${getPercentageClass(m.percentage)}`}>
                      得分率：{m.percentage}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 按知识点分析 */}
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#334155', marginBottom: '12px' }}>
                （二）按知识点统计
              </h3>
              <div className="analysis-grid">
                {reportData.knowledgeAnalysis.slice(0, 6).map((k, idx) => (
                  <div key={idx} className="analysis-item">
                    <div className="analysis-header">{k.knowledgePoint}</div>
                    <div className="analysis-stats">
                      <span>题目数量：{k.count}题</span>
                    </div>
                    <div className="analysis-stats">
                      <span>得分：{k.earned} / {k.max}</span>
                    </div>
                    <div className={`percentage ${getPercentageClass(k.percentage)}`}>
                      得分率：{k.percentage}%
                    </div>
                  </div>
                ))}
              </div>
              {reportData.knowledgeAnalysis.length > 6 && (
                <p style={{ marginTop: '12px', color: '#64748b', fontSize: '13px' }}>
                  * 仅显示前6个知识点，完整分析请查看详细报告
                </p>
              )}
            </div>
          </div>

          {/* 第四部分：教师评价 */}
          <div className="section">
            <div className="section-title">四、教师评价</div>
            <div className="comment-box">
              <div className="comment-label">教师手写评语：</div>
              <div style={{ minHeight: '100px' }}></div>
            </div>
            <div style={{ marginTop: '30px', display: 'flex', justifyContent: 'space-between', paddingTop: '20px', borderTop: '1px solid #e2e8f0' }}>
              <div>
                <span style={{ marginRight: '100px' }}>教师签名：_______________</span>
              </div>
              <div>
                <span>日期：_______________</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
