import Link from "next/link";

export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            small step everyday
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Welcome to Buzzler - Your journey to success starts with small steps
            taken consistently.
          </p>

          <div className="space-x-4">
            <Link
              href="/auth/login"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Login
            </Link>
            <Link
              href="/auth/signup"
              className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-semibold mb-2">Get Started</h3>
            <p className="text-gray-600">
              Begin your journey with simple, actionable steps.
            </p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="text-4xl mb-4">📈</div>
            <h3 className="text-xl font-semibold mb-2">Track Progress</h3>
            <p className="text-gray-600">
              Monitor your growth and celebrate achievements.
            </p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Achieve Goals</h3>
            <p className="text-gray-600">
              Turn your dreams into reality, one step at a time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
