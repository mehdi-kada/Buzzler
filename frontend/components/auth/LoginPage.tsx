'use client';

import React, { useState, FormEvent } from 'react';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface SignupFormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

export const LoginPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  
  // Login form state
  const [loginForm, setLoginForm] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });
  
  // Signup form state
  const [signupForm, setSignupForm] = useState<SignupFormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });

  const handleLoginSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle login logic here
    console.log('Login form submitted:', loginForm);
  };

  const handleSignupSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle signup logic here
    console.log('Signup form submitted:', signupForm);
  };

  const handleSocialLogin = (provider: 'google' | 'github') => {
    // Handle social login logic here
    console.log(`Login with ${provider}`);
  };

  return (
    <div className="bg-black text-white overflow-x-hidden min-h-screen">
      {/* Background */}
      <div className="fixed inset-0 gradient-bg"></div>
      
      {/* Header */}
      <header className="relative z-50 w-full">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <a href="#" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-pink-600 to-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">B</span>
              </div>
              <span className="text-xl font-bold text-white">Buzzler</span>
            </a>
            
            <div className="hidden md:flex items-center space-x-6">
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
              <a href="#" className="text-gray-300 hover:text-white transition-colors">About</a>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="relative z-10 min-h-screen flex items-center justify-center px-6 py-12">
        <div className="max-w-md w-full">
          {/* Auth Card */}
          <div className="auth-card p-8 rounded-2xl">
            {/* Logo & Welcome */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-600 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-float">
                <span className="text-white font-bold text-2xl">B</span>
              </div>
              <h1 className="text-2xl font-bold mb-2">
                Welcome to{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-orange-500 glow-effect">
                  Buzzler
                </span>
              </h1>
              <p className="text-gray-300">Transform your videos into viral social content</p>
            </div>
            
            {/* Tab Toggle */}
            <div className="flex bg-gray-800/50 rounded-lg p-1 mb-6">
              <button 
                onClick={() => setActiveTab('login')}
                className={`tab-button flex-1 font-medium text-center ${
                  activeTab === 'login' ? 'active' : 'text-gray-300'
                }`}
              >
                Sign In
              </button>
              <button 
                onClick={() => setActiveTab('signup')}
                className={`tab-button flex-1 font-medium text-center ${
                  activeTab === 'signup' ? 'active' : 'text-gray-300'
                }`}
              >
                Sign Up
              </button>
            </div>
            
            {/* Login Form */}
            {activeTab === 'login' && (
              <form onSubmit={handleLoginSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                  <input 
                    type="email" 
                    value={loginForm.email}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, email: e.target.value }))}
                    className="form-input w-full px-4 py-3 rounded-lg" 
                    placeholder="Enter your email" 
                    required 
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                  <input 
                    type="password" 
                    value={loginForm.password}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                    className="form-input w-full px-4 py-3 rounded-lg" 
                    placeholder="Enter your password" 
                    required 
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="flex items-center space-x-2">
                    <input 
                      type="checkbox" 
                      checked={loginForm.rememberMe}
                      onChange={(e) => setLoginForm(prev => ({ ...prev, rememberMe: e.target.checked }))}
                      className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500" 
                    />
                    <span className="text-sm text-gray-300">Remember me</span>
                  </label>
                  <a href="#" className="text-sm text-pink-600 hover:text-pink-500">
                    Forgot password?
                  </a>
                </div>
                
                <button type="submit" className="btn-primary w-full px-6 py-3 rounded-lg">
                  Sign In
                </button>
              </form>
            )}
            
            {/* Signup Form */}
            {activeTab === 'signup' && (
              <form onSubmit={handleSignupSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
                    <input 
                      type="text" 
                      value={signupForm.firstName}
                      onChange={(e) => setSignupForm(prev => ({ ...prev, firstName: e.target.value }))}
                      className="form-input w-full px-4 py-3 rounded-lg" 
                      placeholder="John" 
                      required 
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
                    <input 
                      type="text" 
                      value={signupForm.lastName}
                      onChange={(e) => setSignupForm(prev => ({ ...prev, lastName: e.target.value }))}
                      className="form-input w-full px-4 py-3 rounded-lg" 
                      placeholder="Doe" 
                      required 
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                  <input 
                    type="email" 
                    value={signupForm.email}
                    onChange={(e) => setSignupForm(prev => ({ ...prev, email: e.target.value }))}
                    className="form-input w-full px-4 py-3 rounded-lg" 
                    placeholder="Enter your email" 
                    required 
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                  <input 
                    type="password" 
                    value={signupForm.password}
                    onChange={(e) => setSignupForm(prev => ({ ...prev, password: e.target.value }))}
                    className="form-input w-full px-4 py-3 rounded-lg" 
                    placeholder="Create a password" 
                    required 
                  />
                  <p className="text-xs text-gray-400 mt-1">Must be at least 8 characters</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                  <input 
                    type="password" 
                    value={signupForm.confirmPassword}
                    onChange={(e) => setSignupForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    className="form-input w-full px-4 py-3 rounded-lg" 
                    placeholder="Confirm your password" 
                    required 
                  />
                </div>
                
                <div>
                  <label className="flex items-start space-x-2">
                    <input 
                      type="checkbox" 
                      checked={signupForm.agreeToTerms}
                      onChange={(e) => setSignupForm(prev => ({ ...prev, agreeToTerms: e.target.checked }))}
                      className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500 mt-0.5" 
                      required 
                    />
                    <span className="text-sm text-gray-300">
                      I agree to the <a href="#" className="text-pink-600 hover:text-pink-500">Terms of Service</a> and <a href="#" className="text-pink-600 hover:text-pink-500">Privacy Policy</a>
                    </span>
                  </label>
                </div>
                
                <button type="submit" className="btn-primary w-full px-6 py-3 rounded-lg">
                  Create Account
                </button>
              </form>
            )}
            
            {/* Divider */}
            <div className="flex items-center my-6">
              <div className="divider flex-1"></div>
              <span className="px-4 text-sm text-gray-400">or continue with</span>
              <div className="divider flex-1"></div>
            </div>
            
            {/* Social Login */}
            <div className="grid grid-cols-2 gap-3">
              <button 
                onClick={() => handleSocialLogin('google')}
                className="social-btn px-4 py-3 rounded-lg flex items-center justify-center space-x-2"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                <span className="text-sm font-medium">Google</span>
              </button>
              
              <button 
                onClick={() => handleSocialLogin('github')}
                className="social-btn px-4 py-3 rounded-lg flex items-center justify-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.024-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.097.118.112.221.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.758-1.378l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.624 0 11.99-5.367 11.99-11.987C24.007 5.367 18.641.001 12.017.001z"/>
                </svg>
                <span className="text-sm font-medium">GitHub</span>
              </button>
            </div>
            
            {/* Footer Text */}
            <p className="text-center text-sm text-gray-400 mt-6">
              <span>
                {activeTab === 'login' ? "Don't have an account?" : "Already have an account?"}
              </span>
              <button 
                onClick={() => setActiveTab(activeTab === 'login' ? 'signup' : 'login')}
                className="text-pink-600 hover:text-pink-500 ml-1"
              >
                {activeTab === 'login' ? 'Sign up here' : 'Sign in here'}
              </button>
            </p>
          </div>
          
          {/* Features Preview */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-400 mb-4">Join thousands of creators who trust Buzzler</p>
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                <span>AI-Powered Clipping</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                <span>Auto Social Posts</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                <span>Analytics Dashboard</span>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-600 rounded-full opacity-60 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-orange-500 rounded-full opacity-40 animate-pulse animate-delay-1"></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full opacity-50 animate-pulse animate-delay-2"></div>
      </div>
    </div>
  );
};

export default LoginPage;
