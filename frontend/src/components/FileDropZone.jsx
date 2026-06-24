import { UploadCloud } from "lucide-react";

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.webp,.tiff,.bmp";

export default function FileDropZone({ dragging, onDragOver, onDragLeave, onDrop, onPick }) {
  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      data-testid="dropzone"
      className={`bg-slate-50 border-2 border-dashed p-10 md:p-16 text-center transition-colors ${
        dragging ? "border-[#002FA7] bg-blue-50/40" : "border-slate-300"
      }`}
    >
      <UploadCloud className="w-10 h-10 mx-auto text-slate-400" strokeWidth={1.5} />
      <div className="font-display text-xl font-bold text-slate-950 mt-4">
        Drag &amp; drop resumes here
      </div>
      <div className="text-sm text-slate-500 mt-1.5">PDF, JPG, PNG, WEBP — multiple files supported.</div>
      <label className="inline-flex mt-6 cursor-pointer">
        <input
          type="file"
          multiple
          accept={ACCEPT}
          onChange={(e) => onPick(e.target.files)}
          className="hidden"
          data-testid="file-input"
        />
        <span className="inline-flex items-center gap-2 bg-[#002FA7] hover:bg-[#00227A] text-white px-5 py-2.5 text-sm font-semibold transition-colors">
          Browse files
        </span>
      </label>
    </div>
  );
}
