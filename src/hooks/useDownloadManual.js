import { downloadManual } from "../services/apiService";

export const useDownloadManual = () => {
  const handleDownload = async (manual) => {
    try {
      const blob = await downloadManual(manual.id);

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = manual.original_filename;

      document.body.appendChild(link);
      link.click();

      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed", error);
    }
  };

  return { handleDownload };
};
