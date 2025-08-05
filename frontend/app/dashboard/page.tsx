import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              Welcome to Your Dashboard!
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              This is a protected page that requires authentication.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-blue-900 mb-2">
                  Your Progress
                </h3>
                <p className="text-blue-700">
                  Track your daily achievements here.
                </p>
              </div>

              <div className="bg-green-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-green-900 mb-2">
                  Goals
                </h3>
                <p className="text-green-700">Set and manage your goals.</p>
              </div>

              <div className="bg-purple-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-purple-900 mb-2">
                  Analytics
                </h3>
                <p className="text-purple-700">
                  View your performance metrics.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
