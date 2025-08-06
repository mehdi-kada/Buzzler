import React from 'react'

function NavBar() {
  return (
    <nav className="relative z-50 w-full">
    <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-pink-600 to-orange-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">B</span>
                </div>
                <span className="text-xl font-bold text-white">Buzzler</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
                <a href="/" className="nav-link text-gray-300 font-medium">Home</a>
                <a href="#" className="nav-link text-gray-300 font-medium">Features</a>
                <a href="/pricing" className="nav-link text-white font-medium">Pricing</a>
                <a href="/about" className="nav-link text-gray-300 font-medium">About</a>
            </div>
            
            <div className="flex items-center space-x-4">
                <a href="#" className="text-gray-300 hover:text-white transition-colors">Sign in</a>
                <button className="btn-primary px-4 py-2 rounded-lg font-medium text-white">
                    Get Started Free
                </button>
            </div>
        </div>
    </div>
</nav>

  )
}

export default NavBar