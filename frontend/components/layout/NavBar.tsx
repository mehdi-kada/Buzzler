import Link from 'next/link'
import React from 'react'

export default function NavBar() {
  return (
    <nav className="relative z-50 w-full backdrop-blur-lg bg-black/5 ">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-pink-600 to-orange-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">B</span>
            </div>
            <span className="text-xl font-bold text-white">Buzzler</span>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <Link href="/dashboard" className="nav-link text-white font-medium">Dashboard</Link>
            <Link href="/projects" className="nav-link text-gray-300 font-medium">Projects</Link>
            <Link href="/analytics" className="nav-link text-gray-300 font-medium">Analytics</Link>
            <Link href="/settings" className="nav-link text-gray-300 font-medium">Settings</Link>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <button className="w-8 h-8 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">JD</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}