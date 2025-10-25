import { useCallback, useState } from 'react';
import { type ToastProps, type ToastType } from '../components/Toast/Toast';

let toastId = 0;

export const useToast = () => {
  const [toasts, setToasts] = useState<Omit<ToastProps, 'onClose'>[]>([]);

  const showToast = useCallback(
    (type: ToastType, message: string, duration: number = 5000) => {
      const id = `toast-${++toastId}`;
      const newToast: Omit<ToastProps, 'onClose'> = {
        id,
        type,
        message,
        duration,
      };

      setToasts((prev) => [...prev, newToast]);
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return {
    toasts,
    showToast,
    removeToast,
    success: (message: string, duration?: number) =>
      showToast('success', message, duration),
    error: (message: string, duration?: number) =>
      showToast('error', message, duration),
    warning: (message: string, duration?: number) =>
      showToast('warning', message, duration),
    info: (message: string, duration?: number) =>
      showToast('info', message, duration),
  };
};
