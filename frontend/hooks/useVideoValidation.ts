import { videoValidation } from "@/lib/validation/videoValidation";
import { videoValidationConfig, videoValidationResult } from "@/types/video_validation";
import { useCallback, useState } from "react";


export const useVideoValidation = (config: videoValidationConfig) => {
    const [isValidating, setIsValidating] = useState(false);
    const [validationResult, setValidationResult] = useState<videoValidationResult | null>(null);

    const validator = new videoValidation(config);

    const validateVideo = useCallback(async (file: File) => {
        setIsValidating(true);
        try{
            const result = await validator.validateVideo(file);
            setValidationResult(result);
            return result;
        }catch (error) {
            const errorResult: videoValidationResult = {
                isValid: false,
                errors: ["validation failed"],
            };
            setValidationResult(errorResult);
            return errorResult;
        }finally{
            setIsValidating(false);
        }

    }, [validator]);

    const resetValidation = useCallback(() => {
        setValidationResult(null);
        setIsValidating(false);
    }, []);

    return {
        isValidating,
        validationResult,
        validateVideo,
        resetValidation,
    };
};
