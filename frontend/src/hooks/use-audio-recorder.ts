"use client";

import { useState, useRef, useCallback } from "react";
import { GameAPI } from "@/lib/api";

export type RecordingState = "idle" | "recording" | "transcribing";

interface UseAudioRecorderReturn {
  /** Current state of the recorder */
  state: RecordingState;
  /** Start recording from microphone */
  startRecording: () => Promise<void>;
  /** Stop recording, transcribe, and return text */
  stopRecording: () => Promise<string | null>;
  /** Cancel recording without transcribing */
  cancelRecording: () => void;
  /** Error message if something went wrong */
  error: string | null;
  /** Recording duration in seconds */
  duration: number;
}

/**
 * Hook for recording audio from the microphone and transcribing it
 * using Mistral's Voxtral Mini Transcribe via the backend API.
 */
export function useAudioRecorder(): UseAudioRecorderReturn {
  const [state, setState] = useState<RecordingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);

  const cleanup = useCallback(() => {
    // Stop all tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    // Clear timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    mediaRecorderRef.current = null;
    chunksRef.current = [];
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    setDuration(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // Pick a supported MIME type
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")
            ? "audio/ogg;codecs=opus"
            : "audio/mp4";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.start(250); // Collect data every 250ms
      startTimeRef.current = Date.now();
      setState("recording");

      // Update duration every 100ms
      timerRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }, 100);
    } catch (err) {
      const message =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Microphone access denied. Please allow microphone access and try again."
          : "Failed to access microphone. Please check your device settings.";
      setError(message);
      cleanup();
    }
  }, [cleanup]);

  const stopRecording = useCallback(async (): Promise<string | null> => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") {
      cleanup();
      setState("idle");
      return null;
    }

    return new Promise<string | null>((resolve) => {
      recorder.onstop = async () => {
        const mimeType = recorder.mimeType || "audio/webm";
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        cleanup();

        if (audioBlob.size === 0) {
          setError("No audio was recorded.");
          setState("idle");
          resolve(null);
          return;
        }

        setState("transcribing");

        try {
          const result = await GameAPI.transcribeAudio(audioBlob, "en");
          const text = result.text.trim();
          setState("idle");

          if (!text) {
            setError("No speech detected. Please try again.");
            resolve(null);
            return;
          }

          resolve(text);
        } catch (err) {
          console.error("Transcription error:", err);
          setError("Failed to transcribe audio. Please try again.");
          setState("idle");
          resolve(null);
        }
      };

      recorder.stop();
    });
  }, [cleanup]);

  const cancelRecording = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    cleanup();
    setState("idle");
    setError(null);
  }, [cleanup]);

  return {
    state,
    startRecording,
    stopRecording,
    cancelRecording,
    error,
    duration,
  };
}
