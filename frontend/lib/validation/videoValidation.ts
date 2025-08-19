
import { videoMeta, videoValidationResult, videoValidationConfig as videoValidationConfig } from "@/types/video_validation";

export class videoValidation {


    private config: Required<videoValidationConfig>;

    constructor(config: videoValidationConfig) {
        this.config = {
            maxSizeInMB: config.maxSizeInMB ?? 100,
            maxDurationInSeconds: config.maxDurationInSeconds ?? 300,
            allowedFormats: config.allowedFormats ?? ['mp4', 'mov', 'avi', 'webm'],
            minWidth: config.minWidth ?? 320,
            minHeight: config.minHeight ?? 240,
            maxWidth: config.maxWidth ?? 1920,
            maxHeight: config.maxHeight ?? 1080,
        };
    }

    async validateVideo(file: File): Promise<videoValidationResult> {
        const errors: string[] = [];

        if (!file) {
            errors.push("No file provided");
            return { isValid: false, errors };
        }

        
        if (file && file.size > this.config.maxSizeInMB * 1024 * 1024) {
            errors.push(`File is too large. Maximum size is ${this.config.maxSizeInMB}MB`);
            errors.push(`File size must be less than ${this.config.maxSizeInMB}MB`);
        }

        const fileExtension = file.name.split('.').pop()?.toLowerCase();
        if (fileExtension && !this.config.allowedFormats.includes(fileExtension)) {
            errors.push(`Invalid file format. Allowed formats are: ${this.config.allowedFormats.join(', ')}`);
        }
        const videoMetadata = await this.getVideoMetaData(file);
        if (!videoMetadata) {
            errors.push("Could not retrieve video metadata");
            return { isValid: false, errors };
        }
        if (videoMetadata.duration > this.config.maxDurationInSeconds) {
            errors.push(`Video duration exceeds the maximum limit of ${this.config.maxDurationInSeconds} seconds`);
        }

        if (videoMetadata.width < this.config.minWidth || videoMetadata.height < this.config.minHeight) {
            errors.push(`Minimum resolution: ${this.config.minWidth}x${this.config.minHeight}`);
        }

        if (videoMetadata.width > this.config.maxWidth || videoMetadata.height > this.config.maxHeight) {
            errors.push(`Maximum resolution: ${this.config.maxWidth}x${this.config.maxHeight}`);
      }


        return { isValid: errors.length === 0, errors, metadata: videoMetadata };
        
    }

    private getVideoMetaData(file: File): Promise<videoMeta>{
        return new Promise((resolve, reject) =>{
            const video = document.createElement("video")
            const videoURL = URL.createObjectURL(file);

            video.onloadeddata = () => {
                const videoMetadata: videoMeta = {
                    duration: video.duration,
                    width: video.videoWidth,
                    height: video.videoHeight,
                    format: file.type,
                    sizeInMB: file.size / 1024 / 1024,
                    fileName: file.name
                };
                URL.revokeObjectURL(videoURL);
                resolve(videoMetadata);
            };
            video.onerror = () => {
                URL.revokeObjectURL(videoURL);
                reject("Error loading video metadata");
            };

            video.src = videoURL;
            video.load();
        });
    }

}