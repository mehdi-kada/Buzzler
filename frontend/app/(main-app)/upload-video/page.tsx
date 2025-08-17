
import UploadArea from '@/components/upload/UploadArea'
import UploadForm from '@/components/upload/UploadForm'
import ProgressBar from '@/components/upload/ProgressBar'

export const metadata = {
	title: 'Upload Video',
}

export default function UploadVideoPage() {
	return (
		<div className="max-w-4xl mx-auto p-6 space-y-6">
			<h1 className="text-2xl font-semibold">Upload Video</h1>

			<section className="bg-white shadow rounded p-4">
				<h2 className="text-lg font-medium mb-3">Drop or select files</h2>
				<UploadArea />
			</section>

			<section className="bg-white shadow rounded p-4">
				<h2 className="text-lg font-medium mb-3">Details</h2>
				<UploadForm />
			</section>

			<section className="bg-white shadow rounded p-4">
				<h2 className="text-lg font-medium mb-3">Progress</h2>
				<ProgressBar />
			</section>
		</div>
	)
}
