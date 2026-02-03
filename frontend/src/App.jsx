import React, { useEffect, useMemo, useState } from 'react'

const apiBase = ''

const getAuthHeaders = (token) => ({
  Authorization: `Bearer ${token}`
})

const Section = ({ title, children }) => (
  <section className="card">
    <h2>{title}</h2>
    {children}
  </section>
)

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [courses, setCourses] = useState([])
  const [courseName, setCourseName] = useState('')
  const [selectedCourse, setSelectedCourse] = useState(null)
  const [pdfs, setPdfs] = useState([])
  const [query, setQuery] = useState('')
  const [chatAnswer, setChatAnswer] = useState('')
  const [citations, setCitations] = useState([])
  const [message, setMessage] = useState('')
  const [allCourses, setAllCourses] = useState(false)

  const authenticated = useMemo(() => Boolean(token), [token])

  const loadCourses = async () => {
    if (!token) return
    const response = await fetch(`${apiBase}/api/courses`, {
      headers: getAuthHeaders(token)
    })
    if (response.ok) {
      const data = await response.json()
      setCourses(data)
      if (data.length && !selectedCourse) {
        setSelectedCourse(data[0].id)
      }
    }
  }

  const loadPdfs = async (courseId) => {
    if (!token || !courseId) return
    const response = await fetch(`${apiBase}/api/courses/${courseId}/pdfs`, {
      headers: getAuthHeaders(token)
    })
    if (response.ok) {
      setPdfs(await response.json())
    }
  }

  useEffect(() => {
    loadCourses()
  }, [token])

  useEffect(() => {
    if (selectedCourse) {
      loadPdfs(selectedCourse)
    }
  }, [selectedCourse])

  const handleRegister = async () => {
    setMessage('')
    const response = await fetch(`${apiBase}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    if (response.ok) {
      setMessage('Registration successful. You can now log in.')
    } else {
      const data = await response.json()
      setMessage(data.detail || 'Registration failed')
    }
  }

  const handleLogin = async () => {
    setMessage('')
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    const response = await fetch(`${apiBase}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString()
    })
    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
    } else {
      setMessage('Login failed')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken('')
    setCourses([])
    setPdfs([])
    setChatAnswer('')
    setCitations([])
  }

  const handleCreateCourse = async () => {
    if (!courseName) return
    const response = await fetch(`${apiBase}/api/courses`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(token)
      },
      body: JSON.stringify({ name: courseName })
    })
    if (response.ok) {
      setCourseName('')
      await loadCourses()
    }
  }

  const handleDeleteCourse = async (courseId) => {
    const response = await fetch(`${apiBase}/api/courses/${courseId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(token)
    })
    if (response.ok) {
      await loadCourses()
      setSelectedCourse(null)
      setPdfs([])
    }
  }

  const handleUploadPdf = async (event) => {
    const file = event.target.files[0]
    if (!file || !selectedCourse) return
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${apiBase}/api/courses/${selectedCourse}/pdfs`, {
      method: 'POST',
      headers: getAuthHeaders(token),
      body: formData
    })
    if (response.ok) {
      await loadPdfs(selectedCourse)
    } else {
      const data = await response.json()
      setMessage(data.detail || 'Upload failed')
    }
  }

  const handleIngest = async () => {
    if (!selectedCourse) return
    const response = await fetch(`${apiBase}/api/ingest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(token)
      },
      body: JSON.stringify({ course_id: selectedCourse })
    })
    if (response.ok) {
      const data = await response.json()
      setMessage(`Ingested ${data.ingested_pdfs} PDFs into ${data.chunks} chunks.`)
      await loadPdfs(selectedCourse)
    } else {
      const data = await response.json()
      setMessage(data.detail || 'Ingest failed')
    }
  }

  const handleChat = async () => {
    if (!query) return
    const response = await fetch(`${apiBase}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(token)
      },
      body: JSON.stringify({
        query,
        course_id: allCourses ? null : selectedCourse,
        all_courses: allCourses
      })
    })
    if (response.ok) {
      const data = await response.json()
      setChatAnswer(data.answer)
      setCitations(data.citations)
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>Context-Aware Campus Study Assistant</h1>
          <p>Ask questions across your course PDFs with citations.</p>
        </div>
        {authenticated && (
          <button className="secondary" onClick={handleLogout}>Logout</button>
        )}
      </header>

      {!authenticated ? (
        <Section title="Login or Register">
          <div className="form-grid">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="actions">
            <button onClick={handleLogin}>Login</button>
            <button className="secondary" onClick={handleRegister}>Register</button>
          </div>
          {message && <p className="message">{message}</p>}
        </Section>
      ) : (
        <div className="grid">
          <Section title="Courses">
            <div className="form-grid">
              <input
                type="text"
                placeholder="New course name"
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
              />
              <button onClick={handleCreateCourse}>Create</button>
            </div>
            <ul className="list">
              {courses.map((course) => (
                <li key={course.id} className={selectedCourse === course.id ? 'active' : ''}>
                  <button onClick={() => setSelectedCourse(course.id)}>{course.name}</button>
                  <button className="link" onClick={() => handleDeleteCourse(course.id)}>Delete</button>
                </li>
              ))}
            </ul>
          </Section>

          <Section title="PDF Library">
            <p>Upload course PDFs and ingest them for retrieval.</p>
            <input type="file" accept="application/pdf" onChange={handleUploadPdf} />
            <button className="secondary" onClick={handleIngest}>Run Ingestion</button>
            <ul className="list">
              {pdfs.map((pdf) => (
                <li key={pdf.id}>
                  {pdf.filename} {pdf.ingested ? '✅' : '⏳'}
                </li>
              ))}
            </ul>
          </Section>

          <Section title="Chat">
            <label className="checkbox">
              <input
                type="checkbox"
                checked={allCourses}
                onChange={(e) => setAllCourses(e.target.checked)}
              />
              Search across all courses
            </label>
            <textarea
              rows={4}
              placeholder="Ask a study question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={handleChat}>Ask</button>
            {chatAnswer && (
              <div className="chat-output">
                <h3>Answer</h3>
                <p>{chatAnswer}</p>
                {citations.length > 0 && (
                  <div>
                    <h4>Citations</h4>
                    <ul>
                      {citations.map((c) => (
                        <li key={c}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </Section>
        </div>
      )}
    </div>
  )
}
