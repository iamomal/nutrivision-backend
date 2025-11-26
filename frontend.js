import React, { useState, useEffect } from 'react';
import { Camera, TrendingUp, Award, LogOut, Upload, Home, History, User, Menu, X, ChevronRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// API Configuration
const API_BASE = 'http://localhost:5000/api';

// Router Component
const Router = () => {
  const [currentPage, setCurrentPage] = useState('login');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState('');
  const [selectedMeal, setSelectedMeal] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUserId = localStorage.getItem('userId');
    const savedUsername = localStorage.getItem('username');
    
    if (savedToken) {
      setToken(savedToken);
      setUserId(savedUserId);
      setUsername(savedUsername);
      setIsLoggedIn(true);
      setCurrentPage('dashboard');
    }
  }, []);

  const handleLogin = (authToken, authUserId, authUsername) => {
    setToken(authToken);
    setUserId(authUserId);
    setUsername(authUsername);
    setIsLoggedIn(true);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setToken(null);
    setUserId(null);
    setUsername('');
    setIsLoggedIn(false);
    setCurrentPage('login');
    localStorage.clear();
  };

  const navigate = (page) => {
    setCurrentPage(page);
    setSelectedMeal(null);
  };

  const viewMealDetails = (meal) => {
    setSelectedMeal(meal);
    setCurrentPage('meal-details');
  };

  if (!isLoggedIn) {
    return currentPage === 'login' ? (
      <LoginPage onLogin={handleLogin} onNavigate={() => setCurrentPage('register')} />
    ) : (
      <RegisterPage onNavigate={() => setCurrentPage('login')} />
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Sidebar currentPage={currentPage} onNavigate={navigate} onLogout={handleLogout} username={username} />
      <div className="ml-64">
        {currentPage === 'dashboard' && <DashboardPage token={token} />}
        {currentPage === 'upload' && <UploadPage token={token} onSuccess={() => navigate('history')} />}
        {currentPage === 'history' && <HistoryPage token={token} onViewMeal={viewMealDetails} />}
        {currentPage === 'meal-details' && selectedMeal && <MealDetailsPage meal={selectedMeal} />}
        {currentPage === 'profile' && <ProfilePage token={token} username={username} />}
      </div>
    </div>
  );
};

// Login Page Component
const LoginPage = ({ onLogin, onNavigate }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        onLogin(data.token, data.user_id, data.username);
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-emerald-900 flex">
      {/* Left Side - Welcome */}
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center">
              <Camera className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-6xl font-bold text-white mb-4">NutriVision</h1>
          <p className="text-2xl text-green-100">Your personal guide to healthier eating,</p>
          <p className="text-2xl text-green-100">powered by AI.</p>
          
          <div className="mt-16 bg-gradient-to-br from-orange-400 to-orange-500 rounded-3xl p-8 max-w-md mx-auto shadow-2xl">
            <div className="relative">
              <div className="absolute inset-0 flex items-center justify-center opacity-10">
                <div className="text-6xl font-bold text-white">23</div>
              </div>
              <div className="relative z-10 flex items-center justify-center">
                <div className="bg-gray-800 rounded-2xl p-2 transform rotate-12">
                  <div className="w-16 h-28 bg-gray-700 rounded-lg"></div>
                </div>
              </div>
              <div className="mt-8">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100'%3E%3Cellipse cx='100' cy='80' rx='80' ry='20' fill='white'/%3E%3C/svg%3E" alt="plate" className="w-48 h-24 mx-auto" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="w-full max-w-md">
          <div className="bg-gray-800 rounded-3xl shadow-2xl p-12">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Welcome Back</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your username"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your password"
                />
              </div>
              
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-4 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-600 transition disabled:opacity-50 shadow-lg"
              >
                {loading ? 'Logging in...' : 'Login'}
              </button>
              
              <div className="text-center">
                <button
                  onClick={onNavigate}
                  className="text-green-400 hover:text-green-300 text-sm transition"
                >
                  Don't have an account? Sign up
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Register Page Component
const RegisterPage = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Registration successful! Please login.');
        onNavigate();
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-emerald-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-gray-800 rounded-3xl shadow-2xl p-12">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Camera className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white">Create Account</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-4 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-600 transition disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
            
            <div className="text-center">
              <button
                onClick={onNavigate}
                className="text-green-400 hover:text-green-300 text-sm transition"
              >
                Already have an account? Login
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sidebar Component
const Sidebar = ({ currentPage, onNavigate, onLogout, username }) => {
  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
            <Camera className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl font-bold text-white">NutriVision</h1>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <div className="w-12 h-12 bg-gray-600 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-white font-semibold">{username}</p>
            <p className="text-sm text-gray-400">Level 5</p>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 p-4">
        <button
          onClick={() => onNavigate('dashboard')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
            currentPage === 'dashboard' ? 'bg-green-600 text-white' : 'text-gray-300 hover:bg-gray-700'
          }`}
        >
          <Home className="w-5 h-5" />
          <span>Dashboard</span>
        </button>
        
        <button
          onClick={() => onNavigate('upload')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
            currentPage === 'upload' ? 'bg-green-600 text-white' : 'text-gray-300 hover:bg-gray-700'
          }`}
        >
          <Camera className="w-5 h-5" />
          <span>Log Meal</span>
        </button>
        
        <button
          onClick={() => onNavigate('history')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
            currentPage === 'history' ? 'bg-green-600 text-white' : 'text-gray-300 hover:bg-gray-700'
          }`}
        >
          <History className="w-5 h-5" />
          <span>History</span>
        </button>
        
        <button
          onClick={() => onNavigate('profile')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
            currentPage === 'profile' ? 'bg-green-600 text-white' : 'text-gray-300 hover:bg-gray-700'
          }`}
        >
          <User className="w-5 h-5" />
          <span>Profile</span>
        </button>
      </nav>
      
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
        >
          <LogOut className="w-5 h-5" />
          <span>Log Out</span>
        </button>
      </div>
    </div>
  );
};

// Dashboard Page Component  
const DashboardPage = ({ token }) => {
  const [progress, setProgress] = useState(null);
  const [stats, setStats] = useState({
    pointsData: [],
    topFoods: [],
    achievements: []
  });

  useEffect(() => {
    fetchProgress();
    generateMockStats();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await fetch(`${API_BASE}/progress`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setProgress(data);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  };

  const generateMockStats = () => {
    const pointsData = Array.from({ length: 7 }, (_, i) => ({
      day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
      points: Math.floor(Math.random() * 100) + 100
    }));

    setStats({
      pointsData,
      topFoods: [
        { name: 'Lean Meats', percentage: 35 },
        { name: 'Dairy & Eggs', percentage: 25 },
        { name: 'Vegetables', percentage: 20 }
      ],
      achievements: ['streak_keeper', 'healthy_week', 'protein_goal']
    });
  };

  if (!progress) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-white">My Dashboard</h1>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition">Last 7 Days</button>
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition">Last 30 Days</button>
          <button className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition">This Month</button>
        </div>
      </div>

      {/* Goal Progress Cards */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Daily Points Goal</p>
              <p className="text-white text-2xl font-bold">{progress.total_points}/{progress.target} pts</p>
            </div>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${(progress.total_points / progress.target) * 100}%` }}
            ></div>
          </div>
          <p className="text-green-400 text-sm">{progress.target - progress.total_points} points to go!</p>
        </div>

        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Calorie Intake</p>
              <p className="text-white text-2xl font-bold">1800/2200 kcal</p>
            </div>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: '82%' }}></div>
          </div>
          <p className="text-blue-400 text-sm">Keep up the great work!</p>
        </div>

        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Protein Goal</p>
              <p className="text-white text-2xl font-bold">90/120 g</p>
            </div>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
            <div className="bg-purple-500 h-2 rounded-full" style={{ width: '75%' }}></div>
          </div>
          <p className="text-purple-400 text-sm">30g more to build muscle.</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Points Over Time */}
        <div className="col-span-2 bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Points Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.pointsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Line type="monotone" dataKey="points" stroke="#10B981" strokeWidth={3} dot={{ fill: '#10B981', r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Macronutrient Ratio */}
        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Macronutrient Ratio</h2>
          <div className="flex items-center justify-center">
            <div className="relative w-48 h-48">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#4B5563" strokeWidth="20" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#10B981" strokeWidth="20" 
                  strokeDasharray="75 251" strokeDashoffset="0" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#F59E0B" strokeWidth="20" 
                  strokeDasharray="63 251" strokeDashoffset="-75" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#EF4444" strokeWidth="20" 
                  strokeDasharray="63 251" strokeDashoffset="-138" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-white text-xl font-bold">100%</p>
                  <p className="text-gray-400 text-xs">of Macros</p>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6 space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-300 text-sm">Carbs (40%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
              <span className="text-gray-300 text-sm">Protein (30%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-gray-300 text-sm">Fats (30%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-3 gap-6 mt-6">
        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Top Food Categories</h2>
          <div className="space-y-4">
            {stats.topFoods.map((food, idx) => (
              <div key={idx}>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-300">{food.name}</span>
                  <span className="text-green-400">{food.percentage}% of intake</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: `${food.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6">Recent Achievements</h2>
          <div className="flex gap-4">
            <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center">
              <Award className="w-8 h-8 text-white" />
            </div>
            <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center">
              <Award className="w-8 h-8 text-gray-500" />
            </div>
            <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center">
              <Award className="w-8 h-8 text-gray-500" />
            </div>
          </div>
          <p className="text-gray-400 text-sm mt-4">Newest: Streak Keeper - 7 Days!</p>
        </div>

        <div className="bg-gradient-to-br from-green-600 to-emerald-600 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-white font-bold text-lg">Daily Tip</h3>
          </div>
          <p className="text-white text-sm leading-relaxed">
            Hydration is key! Drinking a glass of water before each meal can aid digestion and help you feel full.
          </p>
        </div>
      </div>
    </div>
  );
};

// Upload Page Component
const UploadPage = ({ token, onSuccess }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreview(URL.createObjectURL(file));
      setPrediction(null);
    }
  };

  const analyzeFood = async (mealType) => {
    if (!selectedImage) {
      alert('Please select an image first!');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('meal_type', mealType);

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      const data = await response.json();
      
      if (response.ok) {
        setPrediction(data);
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="inline-block px-4 py-1 bg-yellow-500 rounded-full">
              <span className="text-sm font-semibold text-gray-900">Level 5</span>
            </div>
            <div className="inline-block px-4 py-1 bg-gray-800 rounded-full">
              <span className="text-sm font-semibold text-yellow-500">⭐ 1,250 pts</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Center your meal in the frame</h1>
        </div>

        <div className="bg-gradient-to-br from-cyan-300 to-cyan-500 rounded-3xl p-8 mb-6">
          {preview ? (
            <div className="relative">
              <img src={preview} alt="Preview" className="w-full h-96 object-cover rounded-2xl" />
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setPreview(null);
                  setPrediction(null);
                }}
                className="absolute top-4 right-4 p-2 bg-red-500 rounded-full hover:bg-red-600 transition"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>
          ) : (
            <div className="text-center py-24">
              <div className="w-64 h-64 mx-auto border-4 border-dashed border-white border-opacity-50 rounded-full flex items-center justify-center mb-6">
                <Camera className="w-24 h-24 text-white opacity-50" />
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
                id="meal-upload"
              />
              <label
                htmlFor="meal-upload"
                className="inline-block px-8 py-4 bg-white text-cyan-600 font-semibold rounded-xl cursor-pointer hover:bg-gray-100 transition"
              >
                Select Image
              </label>
            </div>
          )}
        </div>

        {selectedImage && !prediction && (
          <div>
            <div className="flex gap-2 justify-center mb-4">
              <button className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition">
                Single Item
              </button>
              <button className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition">
                Full Plate
              </button>
            </div>
            
            <div className="bg-gray-800 rounded-2xl p-6 mb-6 border border-gray-700">
              <p className="text-gray-400 mb-4">Today's Intake</p>
              <p className="text-white text-xl">1200 Cal | 80g Protein</p>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => analyzeFood('breakfast')}
                disabled={loading}
                className="px-8 py-3 bg-yellow-500 text-gray-900 font-semibold rounded-xl hover:bg-yellow-400 transition disabled:opacity-50"
              >
                Breakfast
              </button>
              <button
                onClick={() => analyzeFood('lunch')}
                disabled={loading}
                className="px-8 py-3 bg-orange-500 text-white font-semibold rounded-xl hover:bg-orange-400 transition disabled:opacity-50"
              >
                Lunch
              </button>
              <button
                onClick={() => analyzeFood('dinner')}
                disabled={loading}
                className="px-8 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-400 transition disabled:opacity-50"
              >
                Dinner
              </button>
              <button
                onClick={() => analyzeFood('snack')}
                disabled={loading}
                className="px-8 py-3 bg-green-500 text-white font-semibold rounded-xl hover:bg-green-400 transition disabled:opacity-50"
              >
                Snack
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-500 mx-auto mb-4"></div>
            <p className="text-white text-lg">Analyzing your meal...</p>
          </div>
        )}

        {prediction && (
          <div className="bg-green-900 bg-opacity-50 border border-green-500 rounded-2xl p-8">
            <div className="text-center mb-6">
              <div className="inline-block px-6 py-2 bg-green-500 rounded-full mb-4">
                <span className="text-2xl font-bold text-white">+{prediction.points_awarded} Points</span>
              </div>
              <p className="text-green-300">Great choice for your protein goal!</p>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 mb-4">
              <h3 className="text-xl font-bold text-white mb-4">{prediction.food_name}</h3>
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-gray-400 text-sm mb-1">Calories</p>
                  <p className="text-white text-2xl font-bold">{prediction.nutrition.calories}</p>
                  <p className="text-gray-400 text-xs">kcal</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400 text-sm mb-1">Protein</p>
                  <p className="text-white text-2xl font-bold">{prediction.nutrition.protein}</p>
                  <p className="text-gray-400 text-xs">g</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400 text-sm mb-1">Carbs</p>
                  <p className="text-white text-2xl font-bold">{prediction.nutrition.carbs}</p>
                  <p className="text-gray-400 text-xs">g</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400 text-sm mb-1">Fat</p>
                  <p className="text-white text-2xl font-bold">{prediction.nutrition.fat}</p>
                  <p className="text-gray-400 text-xs">g</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm">Confidence: {(prediction.confidence * 100).toFixed(1)}%</p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={onSuccess}
                className="flex-1 py-4 bg-green-500 text-white font-semibold rounded-xl hover:bg-green-600 transition"
              >
                ✓ Log Food
              </button>
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setPreview(null);
                  setPrediction(null);
                }}
                className="flex-1 py-4 bg-gray-700 text-white font-semibold rounded-xl hover:bg-gray-600 transition"
              >
                Discard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// History Page Component
const HistoryPage = ({ token, onViewMeal }) => {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('week');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch(`${API_BASE}/logs?limit=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setLogs(data.logs);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  const groupedLogs = logs.reduce((acc, log) => {
    const date = new Date(log.logged_at).toLocaleDateString('en-US', { 
      weekday: 'long', 
      month: 'long', 
      day: 'numeric' 
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(log);
    return acc;
  }, {});

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">Meal History</h1>
        <p className="text-gray-400 mb-8">Review your previously analyzed meals and track your progress.</p>

        <div className="flex gap-4 mb-8">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search for a food item..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-6 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <button
            onClick={() => setFilter('week')}
            className={`px-6 py-3 rounded-xl font-semibold transition ${
              filter === 'week' ? 'bg-green-500 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setFilter('month')}
            className={`px-6 py-3 rounded-xl font-semibold transition ${
              filter === 'month' ? 'bg-green-500 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            This Month
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-6 py-3 rounded-xl font-semibold transition ${
              filter === 'all' ? 'bg-green-500 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Last 3 Months
          </button>
        </div>

        <div className="space-y-8">
          {Object.entries(groupedLogs).map(([date, meals]) => (
            <div key={date}>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">{date}</h2>
              <div className="space-y-4">
                {meals.map((meal) => (
                  <div
                    key={meal.log_id}
                    onClick={() => onViewMeal(meal)}
                    className="bg-gray-800 rounded-2xl p-6 border border-gray-700 hover:border-green-500 transition cursor-pointer group"
                  >
                    <div className="flex items-center gap-6">
                      <div className="w-32 h-32 bg-gray-700 rounded-xl overflow-hidden flex-shrink-0">
                        {meal.image_path ? (
                          <>
                            <img 
                              src={`http://localhost:5000/uploads/${meal.image_path}`}
                              alt={meal.food_name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.parentElement.querySelector('.fallback-icon').style.display = 'flex';
                              }}
                            />
                            <div className="fallback-icon w-full h-full bg-gradient-to-br from-green-400 to-blue-500 items-center justify-center" style={{ display: 'none' }}>
                              <span className="text-4xl">🍽️</span>
                            </div>
                          </>
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center">
                            <span className="text-4xl">🍽️</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-white mb-1">
                              {meal.food_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h3>
                            <p className="text-gray-400 text-sm">
                              {new Date(meal.logged_at).toLocaleTimeString('en-US', { 
                                hour: 'numeric', 
                                minute: '2-digit' 
                              })}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className={`text-2xl font-bold ${
                              meal.points_awarded > 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {meal.points_awarded > 0 ? '+' : ''}{meal.points_awarded} Points
                            </span>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-4 gap-4">
                          <div>
                            <p className="text-gray-500 text-xs mb-1">Calories</p>
                            <p className="text-white font-semibold">{meal.calories}</p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs mb-1">Protein</p>
                            <p className="text-white font-semibold">{meal.protein}g</p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs mb-1">Carbs</p>
                            <p className="text-white font-semibold">{meal.carbs}g</p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs mb-1">Fat</p>
                            <p className="text-white font-semibold">{meal.fat}g</p>
                          </div>
                        </div>
                      </div>
                      
                      <button className="text-green-400 opacity-0 group-hover:opacity-100 transition">
                        <span className="text-sm font-semibold flex items-center gap-2">
                          View Details
                          <ChevronRight className="w-5 h-5" />
                        </span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {logs.length === 0 && (
          <div className="text-center py-16">
            <Camera className="w-24 h-24 text-gray-700 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No meals logged yet</h3>
            <p className="text-gray-500">Start analyzing your meals to see them here!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Meal Details Page Component
const MealDetailsPage = ({ meal }) => {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-2 gap-8">
          <div>
            <div className="bg-gray-800 rounded-3xl overflow-hidden mb-6 border border-gray-700">
              <div className="h-96 relative">
                {meal.image_path ? (
                  <>
                    <img 
                      src={`http://localhost:5000/uploads/${meal.image_path}`}
                      alt={meal.food_name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.querySelector('.fallback-bg').style.display = 'flex';
                      }}
                    />
                    <div className="fallback-bg absolute inset-0 bg-gradient-to-br from-green-400 to-blue-500 items-center justify-center" style={{ display: 'none' }}>
                      <span className="text-8xl">🍽️</span>
                    </div>
                  </>
                ) : (
                  <div className="absolute inset-0 bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center">
                    <span className="text-8xl">🍽️</span>
                  </div>
                )}
              </div>
            </div>
            
            <h1 className="text-4xl font-bold text-white mb-2">
              {meal.food_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h1>
            <p className="text-gray-400 mb-6">
              {new Date(meal.logged_at).toLocaleString('en-US', { 
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit'
              })}
            </p>

            <div className="bg-green-900 bg-opacity-30 border border-green-500 rounded-2xl p-6 mb-6">
              <div className="text-center">
                <div className="text-5xl font-bold text-green-400 mb-2">
                  {meal.points_awarded > 0 ? '+' : ''}{meal.points_awarded} Points
                </div>
                <p className="text-green-300">Great choice for your protein goal!</p>
              </div>
            </div>

            <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Total Points</h3>
              <div className="text-center">
                <div className="text-4xl font-bold text-white mb-2">1,250</div>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500 bg-opacity-20 rounded-full">
                  <span className="text-yellow-500">⭐</span>
                  <span className="text-yellow-500 font-semibold">Level 5</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700 mb-6">
              <h2 className="text-2xl font-bold text-white mb-6">Nutritional Information</h2>
              
              <div className="grid grid-cols-2 gap-6 mb-8">
                <div className="bg-gray-900 rounded-xl p-6 text-center">
                  <p className="text-gray-400 text-sm mb-2">Calories</p>
                  <p className="text-4xl font-bold text-white mb-1">{meal.calories}</p>
                  <p className="text-gray-400 text-sm">kcal</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-6 text-center">
                  <p className="text-gray-400 text-sm mb-2">Protein</p>
                  <p className="text-4xl font-bold text-white mb-1">{meal.protein}</p>
                  <p className="text-gray-400 text-sm">g</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-6 text-center">
                  <p className="text-gray-400 text-sm mb-2">Carbs</p>
                  <p className="text-4xl font-bold text-white mb-1">{meal.carbs}</p>
                  <p className="text-gray-400 text-sm">g</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-6 text-center">
                  <p className="text-gray-400 text-sm mb-2">Fat</p>
                  <p className="text-4xl font-bold text-white mb-1">{meal.fat}</p>
                  <p className="text-gray-400 text-sm">g</p>
                </div>
              </div>

              <div className="border-t border-gray-700 pt-6">
                <h3 className="text-lg font-semibold text-white mb-4">Macronutrients</h3>
                <div className="relative w-48 h-48 mx-auto mb-6">
                  <svg viewBox="0 0 100 100" className="transform -rotate-90">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#1F2937" strokeWidth="20" />
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#3B82F6" strokeWidth="20" 
                      strokeDasharray="100 251" strokeDashoffset="0" />
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#F59E0B" strokeWidth="20" 
                      strokeDasharray="75 251" strokeDashoffset="-100" />
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#A855F7" strokeWidth="20" 
                      strokeDasharray="76 251" strokeDashoffset="-175" />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-white text-2xl font-bold">100%</p>
                      <p className="text-gray-400 text-xs">of Macros</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                      <span className="text-gray-300">Protein</span>
                    </div>
                    <span className="text-white font-semibold">40%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
                      <span className="text-gray-300">Carbs</span>
                    </div>
                    <span className="text-white font-semibold">30%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-purple-500 rounded-full"></div>
                      <span className="text-gray-300">Fat</span>
                    </div>
                    <span className="text-white font-semibold">30%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Micronutrients</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Saturated Fat</span>
                  <span className="text-white font-semibold">3g</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sodium</span>
                  <span className="text-white font-semibold">600mg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Fiber</span>
                  <span className="text-white font-semibold">5g</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sugar</span>
                  <span className="text-white font-semibold">8g</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Vitamin C</span>
                  <span className="text-white font-semibold">30% DV</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mt-8">
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4">Daily Goal Progress</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Calories</span>
                  <span className="text-white font-semibold">950 / 2000 kcal</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '47%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Protein</span>
                  <span className="text-white font-semibold">80 / 120 g</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '67%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Carbs</span>
                  <span className="text-white font-semibold">115 / 150 g</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-orange-500 h-2 rounded-full" style={{ width: '77%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Sugar Limit</span>
                  <span className="text-white font-semibold">28 / 25 g</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button className="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-4 rounded-xl transition">
              ✓ Log Food
            </button>
            <button className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-4 rounded-xl transition">
              Discard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Page Component
const ProfilePage = ({ token, username }) => {
  const [profileData, setProfileData] = useState({
    username: username,
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);

  useEffect(() => {
    fetchUserData();
    fetchProfilePicture();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${API_BASE}/user/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setProfileData(prev => ({
          ...prev,
          username: data.username,
          email: data.email
        }));
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const fetchProfilePicture = async () => {
    try {
      const response = await fetch(`${API_BASE}/user/profile-picture`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        if (data.profile_picture) {
          setImagePreview(`http://localhost:5000/uploads/${data.profile_picture}`);
        }
      }
    } catch (error) {
      console.error('Failed to fetch profile picture:', error);
    }
  };

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfileImage(file);
      const preview = URL.createObjectURL(file);
      setImagePreview(preview);
      
      // Upload immediately
      const formData = new FormData();
      formData.append('image', file);
      
      try {
        const response = await fetch(`${API_BASE}/user/upload-profile-picture`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          setImagePreview(`http://localhost:5000/uploads/${data.filename}`);
          alert('Profile picture updated!');
        }
      } catch (error) {
        alert('Failed to upload profile picture');
      }
    }
  };

  const handleDeleteImage = () => {
    setProfileImage(null);
    setImagePreview(null);
  };

  const handleSaveChanges = async () => {
    try {
      const response = await fetch(`${API_BASE}/user/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: profileData.username,
          email: profileData.email
        })
      });

      if (response.ok) {
        alert('Profile updated successfully!');
        setIsEditing(false);
      } else {
        alert('Failed to update profile');
      }
    } catch (error) {
      alert('Error updating profile');
    }
  };

  const handlePasswordChange = async () => {
    if (profileData.newPassword !== profileData.confirmPassword) {
      alert('New passwords do not match!');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/user/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: profileData.currentPassword,
          new_password: profileData.newPassword
        })
      });

      if (response.ok) {
        alert('Password changed successfully!');
        setShowPasswordChange(false);
        setProfileData(prev => ({
          ...prev,
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }));
      } else {
        const data = await response.json();
        alert(data.message || 'Failed to change password');
      }
    } catch (error) {
      alert('Error changing password');
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Profile & Account</h1>
        <p className="text-gray-400 mb-8">Update your photo and personal details here.</p>

        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700 mb-6">
          <h2 className="text-xl font-bold text-white mb-6">Update your photo</h2>
          <p className="text-gray-400 mb-6">This will be displayed on your profile.</p>
          
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 bg-gray-700 rounded-full flex items-center justify-center overflow-hidden">
              {imagePreview ? (
                <img src={imagePreview} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User className="w-12 h-12 text-gray-500" />
              )}
            </div>
            <div className="flex gap-3">
              <button 
                onClick={handleDeleteImage}
                className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
              >
                Delete
              </button>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
                id="profile-image-upload"
              />
              <label
                htmlFor="profile-image-upload"
                className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition cursor-pointer"
              >
                Upload Image
              </label>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700 mb-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">Personal Information</h2>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition text-sm"
            >
              {isEditing ? 'Cancel Edit' : 'Edit Info'}
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Username</label>
              <input
                type="text"
                value={profileData.username}
                onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                disabled={!isEditing}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Email Address</label>
              <input
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                disabled={!isEditing}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700 mb-6">
          <h2 className="text-xl font-bold text-white mb-2">Password</h2>
          <p className="text-gray-400 mb-6">It's a good idea to use a strong password that you're not using elsewhere.</p>
          
          {!showPasswordChange ? (
            <button 
              onClick={() => setShowPasswordChange(true)}
              className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
            >
              Change Password
            </button>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Current Password</label>
                <input
                  type="password"
                  value={profileData.currentPassword}
                  onChange={(e) => setProfileData({...profileData, currentPassword: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter current password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">New Password</label>
                <input
                  type="password"
                  value={profileData.newPassword}
                  onChange={(e) => setProfileData({...profileData, newPassword: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter new password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Confirm New Password</label>
                <input
                  type="password"
                  value={profileData.confirmPassword}
                  onChange={(e) => setProfileData({...profileData, confirmPassword: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Confirm new password"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handlePasswordChange}
                  className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition"
                >
                  Update Password
                </button>
                <button
                  onClick={() => setShowPasswordChange(false)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {isEditing && (
          <div className="flex justify-end gap-4">
            <button 
              onClick={() => setIsEditing(false)}
              className="px-8 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-xl transition"
            >
              Cancel
            </button>
            <button 
              onClick={handleSaveChanges}
              className="px-8 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition"
            >
              Save Changes
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Router;