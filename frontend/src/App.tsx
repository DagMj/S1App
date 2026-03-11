import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/AppLayout'
import { ExamPage } from './pages/ExamPage'
import { ModesPage } from './pages/ModesPage'
import { ResultsPage } from './pages/ResultsPage'
import { SubjectSelectionPage } from './pages/SubjectSelectionPage'
import { TrainingPage } from './pages/TrainingPage'

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<SubjectSelectionPage />} />
        <Route path="/s1" element={<ModesPage />} />
        <Route path="/exam" element={<ExamPage />} />
        <Route path="/training" element={<TrainingPage />} />
        <Route path="/results/:sessionId" element={<ResultsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  )
}
