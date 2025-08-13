import { ProtectedRoute } from "@/components/auth/ProtectedRoute";


export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-black text-white overflow-x-hidden">
        {/* Background */}
        <div className="fixed inset-0 gradient-bg"></div>
        
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-600 rounded-full opacity-60 animate-pulse"></div>
          <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-orange-500 rounded-full opacity-40 animate-pulse animate-delay-1"></div>
          <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full opacity-50 animate-pulse animate-delay-2"></div>
        </div>
        
        <main className="relative z-10 pt-8 pb-16 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  Welcome back, <span className="gradient-text glow-effect">John</span>
                </h1>
                <p className="text-gray-300">Transform your long videos into viral social content</p>
              </div>
              <button className="btn-primary px-6 py-3 rounded-lg font-semibold text-white mt-4 md:mt-0">
                + New Project
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="stats-card p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-300 text-sm">Total Videos</p>
                    <p className="text-2xl font-bold">24</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="stats-card p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-300 text-sm">Clips Generated</p>
                    <p className="text-2xl font-bold">156</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 7H7v10h2V7zm6 0h-2v10h2V7zm4-4H5c-.55 0-1 .45-1 1s.45 1 1 1h14c.55 0 1-.45 1-1s-.45-1-1-1z"/>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="stats-card p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-300 text-sm">Posts Published</p>
                    <p className="text-2xl font-bold">89</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 16H5V6h14v12z"/>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="stats-card p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-300 text-sm">Total Views</p>
                    <p className="text-2xl font-bold">12.5K</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Recent Projects</h2>
                <a href="#" className="text-pink-600 hover:text-pink-500 font-medium">View All →</a>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="project-card p-6 rounded-xl">
                  <div className="aspect-video bg-gray-800 rounded-lg mb-4 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-pink-600/20 to-orange-500/20"></div>
                    <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs">
                      12:34
                    </div>
                  </div>
                  <h3 className="font-semibold mb-2">Podcast Episode #45</h3>
                  <p className="text-gray-300 text-sm mb-3">AI and the Future of Development</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">
                      8 clips generated
                    </span>
                    <span className="text-xs text-gray-400">2 days ago</span>
                  </div>
                </div>
                
                <div className="project-card p-6 rounded-xl">
                  <div className="aspect-video bg-gray-800 rounded-lg mb-4 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-pink-600/20 to-orange-500/20"></div>
                    <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs">
                      8:45
                    </div>
                  </div>
                  <h3 className="font-semibold mb-2">Product Demo Video</h3>
                  <p className="text-gray-300 text-sm mb-3">New Feature Showcase</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded">
                      Processing...
                    </span>
                    <span className="text-xs text-gray-400">1 hour ago</span>
                  </div>
                </div>
                
                <div className="project-card p-6 rounded-xl">
                  <div className="aspect-video bg-gray-800 rounded-lg mb-4 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-pink-600/20 to-orange-500/20"></div>
                    <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs">
                      25:12
                    </div>
                  </div>
                  <h3 className="font-semibold mb-2">Webinar Recording</h3>
                  <p className="text-gray-300 text-sm mb-3">Marketing Strategies 2024</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">
                      12 clips generated
                    </span>
                    <span className="text-xs text-gray-400">1 week ago</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="project-card p-8 rounded-xl">
                <h3 className="text-xl font-bold mb-4 gradient-text">
                  Upload New Video
                </h3>
                <p className="text-gray-300 mb-6">Upload a video file or paste a URL from YouTube, Vimeo, or other platforms</p>
                <div className="flex space-x-4">
                  <button className="btn-primary px-4 py-2 rounded-lg font-medium text-white">
                    Upload File
                  </button>
                  <button className="btn-secondary px-4 py-2 rounded-lg font-medium text-white">
                    From URL
                  </button>
                </div>
              </div>
              
              <div className="project-card p-8 rounded-xl">
                <h3 className="text-xl font-bold mb-4 gradient-text">
                  Recent Activity
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-300">Podcast Episode #45 clips published to Twitter</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-300">Product Demo transcription completed</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <span className="text-sm text-gray-300">Webinar Recording analytics updated</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
