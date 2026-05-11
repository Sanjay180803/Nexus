import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [page, setPage] = useState('login')
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [projects, setProjects] = useState([])
  const [tasks, setTasks] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [error, setError] = useState('')

  const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    headers: { Authorization: `Bearer ${token}` }
  })

  useEffect(() => {
    if (token) {
      setPage('projects')
      fetchProjects()
    }
  }, [token])

  const fetchProjects = async () => {
    try {
      const res = await api.get('/projects/')
      setProjects(res.data)
    } catch { setError('Failed to load projects') }
  }

  const fetchTasks = async (projectId) => {
    try {
      const res = await api.get(`/tasks/${projectId}/tasks`)
      setTasks(res.data)
    } catch { setError('Failed to load tasks') }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    const email = e.target.email.value
    const password = e.target.password.value
    try {
      const res = await axios.post('http://127.0.0.1:8000/auth/login', { email, password })
      localStorage.setItem('token', res.data.access_token)
      setToken(res.data.access_token)
      setError('')
    } catch { setError('Invalid email or password') }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    const email = e.target.email.value
    const username = e.target.username.value
    const password = e.target.password.value
    try {
      await axios.post('http://127.0.0.1:8000/auth/register', { email, username, password })
      setPage('login')
      setError('Account created! Please login.')
    } catch { setError('Registration failed') }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    const name = e.target.name.value
    const description = e.target.description.value
    try {
      await api.post('/projects/', { name, description })
      e.target.reset()
      fetchProjects()
    } catch { setError('Failed to create project') }
  }

  const handleCreateTask = async (e) => {
    e.preventDefault()
    const title = e.target.title.value
    const description = e.target.description.value
    try {
      await api.post(`/tasks/${selectedProject.id}/tasks`, { title, description })
      e.target.reset()
      fetchTasks(selectedProject.id)
    } catch { setError('Failed to create task') }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken('')
    setPage('login')
    setProjects([])
    setTasks([])
    setSelectedProject(null)
  }

  const priorityColor = (p) => ({
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }[p] || 'bg-gray-100')

  if (page === 'login') return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-2xl w-96 shadow-xl">
        <h1 className="text-3xl font-bold text-white mb-2">Nexus</h1>
        <p className="text-gray-400 mb-6">AI-Powered Project Manager</p>
        {error && <p className="text-red-400 mb-4 text-sm">{error}</p>}
        <form onSubmit={handleLogin} className="space-y-4">
          <input name="email" type="email" placeholder="Email" required
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          <input name="password" type="password" placeholder="Password" required
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition">
            Login
          </button>
        </form>
        <p className="text-gray-400 mt-4 text-center text-sm">
          No account?{' '}
          <button onClick={() => { setPage('register'); setError('') }}
            className="text-blue-400 hover:underline">Register</button>
        </p>
      </div>
    </div>
  )

  if (page === 'register') return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-2xl w-96 shadow-xl">
        <h1 className="text-3xl font-bold text-white mb-6">Create Account</h1>
        {error && <p className="text-red-400 mb-4 text-sm">{error}</p>}
        <form onSubmit={handleRegister} className="space-y-4">
          <input name="email" type="email" placeholder="Email" required
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          <input name="username" placeholder="Username" required
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          <input name="password" type="password" placeholder="Password" required
            className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition">
            Register
          </button>
        </form>
        <p className="text-gray-400 mt-4 text-center text-sm">
          Have an account?{' '}
          <button onClick={() => { setPage('login'); setError('') }}
            className="text-blue-400 hover:underline">Login</button>
        </p>
      </div>
    </div>
  )

  if (page === 'projects') return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="bg-gray-900 px-8 py-4 flex justify-between items-center border-b border-gray-800">
        <h1 className="text-xl font-bold text-blue-400">Nexus</h1>
        <button onClick={handleLogout}
          className="text-gray-400 hover:text-white text-sm transition">Logout</button>
      </nav>
      <div className="max-w-4xl mx-auto p-8">
        <h2 className="text-2xl font-bold mb-6">Your Projects</h2>
        <form onSubmit={handleCreateProject} className="flex gap-3 mb-8">
          <input name="name" placeholder="Project name" required
            className="bg-gray-800 px-4 py-2 rounded-lg flex-1 outline-none focus:ring-2 focus:ring-blue-500" />
          <input name="description" placeholder="Description"
            className="bg-gray-800 px-4 py-2 rounded-lg flex-1 outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="submit"
            className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-semibold transition">
            Create
          </button>
        </form>
        {error && <p className="text-red-400 mb-4 text-sm">{error}</p>}
        <div className="grid gap-4">
          {projects.map(p => (
            <div key={p.id} onClick={() => { setSelectedProject(p); fetchTasks(p.id); setPage('tasks') }}
              className="bg-gray-900 p-6 rounded-xl border border-gray-800 hover:border-blue-500 cursor-pointer transition">
              <h3 className="text-lg font-semibold">{p.name}</h3>
              <p className="text-gray-400 text-sm mt-1">{p.description}</p>
            </div>
          ))}
          {projects.length === 0 &&
            <p className="text-gray-500 text-center py-12">No projects yet. Create one above!</p>}
        </div>
      </div>
    </div>
  )

  if (page === 'tasks') return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="bg-gray-900 px-8 py-4 flex justify-between items-center border-b border-gray-800">
        <div className="flex items-center gap-4">
          <button onClick={() => setPage('projects')} className="text-gray-400 hover:text-white transition">← Back</button>
          <h1 className="text-xl font-bold text-blue-400">{selectedProject?.name}</h1>
        </div>
        <button onClick={handleLogout} className="text-gray-400 hover:text-white text-sm transition">Logout</button>
      </nav>
      <div className="max-w-4xl mx-auto p-8">
        <h2 className="text-2xl font-bold mb-2">Tasks</h2>
        <p className="text-gray-400 text-sm mb-6">AI automatically assigns priority based on your task description</p>
        <form onSubmit={handleCreateTask} className="flex gap-3 mb-8">
          <input name="title" placeholder="Task title" required
            className="bg-gray-800 px-4 py-2 rounded-lg flex-1 outline-none focus:ring-2 focus:ring-blue-500" />
          <input name="description" placeholder="Describe the task (AI will set priority)"
            className="bg-gray-800 px-4 py-2 rounded-lg flex-1 outline-none focus:ring-2 focus:ring-blue-500" />
          <button type="submit"
            className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-semibold transition">
            Add
          </button>
        </form>
        {error && <p className="text-red-400 mb-4 text-sm">{error}</p>}
        <div className="grid gap-4">
          {tasks.map(t => (
            <div key={t.id} className="bg-gray-900 p-6 rounded-xl border border-gray-800">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{t.title}</h3>
                  <p className="text-gray-400 text-sm mt-1">{t.description}</p>
                </div>
                <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase ${priorityColor(t.priority)}`}>
                  {t.priority}
                </span>
              </div>
            </div>
          ))}
          {tasks.length === 0 &&
            <p className="text-gray-500 text-center py-12">No tasks yet. Add one above!</p>}
        </div>
      </div>
    </div>
  )
}

export default App