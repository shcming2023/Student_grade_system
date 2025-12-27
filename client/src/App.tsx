import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import ExamTemplateDetail from "./pages/ExamTemplateDetail";
import ReportCard from "./pages/ReportCard";
import Students from "./pages/Students";
import Classes from "./pages/Classes";
import Subjects from "./pages/Subjects";
import ExamTemplates from "./pages/ExamTemplates";
import ScoreEntry from "./pages/ScoreEntry";
import Scores from "./pages/Scores";
import TeacherLogin from "./pages/TeacherLogin";
import Teachers from "./pages/Teachers";
import ExamSessions from "./pages/ExamSessions";
import ProtectedRoute from "./components/ProtectedRoute";

function Router() {
  return (
    <Switch>
      {/* 公开路由：登录页 */}
      <Route path={"/teacher-login"} component={TeacherLogin} />
      
      {/* 受保护的路由：需要登录 */}
      <Route path={"/"}>
        <ProtectedRoute>
          <Home />
        </ProtectedRoute>
      </Route>
      <Route path={"/students"}>
        <ProtectedRoute>
          <Students />
        </ProtectedRoute>
      </Route>
      <Route path={"/classes"}>
        <ProtectedRoute>
          <Classes />
        </ProtectedRoute>
      </Route>
      <Route path={"/subjects"}>
        <ProtectedRoute>
          <Subjects />
        </ProtectedRoute>
      </Route>
      <Route path={"/teachers"}>
        <ProtectedRoute>
          <Teachers />
        </ProtectedRoute>
      </Route>
      <Route path={"/exam-sessions"}>
        <ProtectedRoute>
          <ExamSessions />
        </ProtectedRoute>
      </Route>
      <Route path={"/exam-templates"}>
        <ProtectedRoute>
          <ExamTemplates />
        </ProtectedRoute>
      </Route>
      <Route path="/exam-templates/:id">
        <ProtectedRoute>
          <ExamTemplateDetail />
        </ProtectedRoute>
      </Route>
      <Route path={"/score-entry"}>
        <ProtectedRoute>
          <ScoreEntry />
        </ProtectedRoute>
      </Route>
      <Route path={"/scores"}>
        <ProtectedRoute>
          <Scores />
        </ProtectedRoute>
      </Route>
      <Route path="/report-card/:examId/:studentId">
        <ProtectedRoute>
          <ReportCard />
        </ProtectedRoute>
      </Route>
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
