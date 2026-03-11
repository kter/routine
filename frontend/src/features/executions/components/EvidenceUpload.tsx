import { useState, useRef } from "react";
import { Upload, CheckCircle } from "lucide-react";
import { executionsApi } from "@/lib/api/executions";

interface EvidenceUploadProps {
  executionId: string;
  stepId: string;
  onUploaded: (key: string) => void;
}

export function EvidenceUpload({
  executionId,
  stepId,
  onUploaded,
}: EvidenceUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedKey, setUploadedKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    try {
      const { uploadUrl, key } = await executionsApi.getEvidenceUploadUrl(
        executionId,
        stepId,
        file.type,
      );
      await fetch(uploadUrl, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type },
      });
      setUploadedKey(key);
      onUploaded(key);
    } catch {
      setError("アップロードに失敗しました");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">証跡画像 *</label>
      {uploadedKey ? (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <CheckCircle className="h-4 w-4" />
          アップロード完了
        </div>
      ) : (
        <div>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 rounded-md border border-dashed px-4 py-3 text-sm text-muted-foreground hover:border-primary hover:text-primary disabled:opacity-50"
          >
            <Upload className="h-4 w-4" />
            {isUploading ? "アップロード中..." : "画像を選択"}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
      )}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
