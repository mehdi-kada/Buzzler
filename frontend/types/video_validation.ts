export interface videoValidation {
    maxSizeInMB?: number;
    maxDurationInSeconds?: number;
    allowedFormats?: string[];
    minWidth?: number;
    minHeight?: number;
    maxWidth?: number;
    maxHeight?: number;
}

export interface videoMeta{
    duration: number;
    height: number;
    width: number;
    format: string;
    sizeInMB: number;
    fileName: string;
}

export interface videoValidationResult {
    isValid: boolean;
    errors: string[];
    metadata?: videoMeta;
}

