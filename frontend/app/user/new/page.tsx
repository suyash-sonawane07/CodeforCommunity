'use client';
import { useState, useRef } from 'react';
import { useCreateRequest } from '@/hooks';
import { useTranslation } from '@/hooks/useTranslation';
import { useRouter } from 'next/navigation';

export default function NewRequest() {
  const router = useRouter();
  const { create, loading, error } = useCreateRequest();
  const { t, lang } = useTranslation();
  
  const [channel, setChannel] = useState<'text' | 'voice'>('text');
  const [text, setText] = useState('');
  const [locationText, setLocationText] = useState('');
  const [consentAck, setConsentAck] = useState(false);
  
  const [recording, setRecording] = useState(false);
  const [audioBase64, setAudioBase64] = useState<string | null>(null);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunks.current = [];
      mediaRecorder.current.ondataavailable = (e) => audioChunks.current.push(e.data);
      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
          const base64data = reader.result?.toString().split(',')[1];
          if (base64data) setAudioBase64(base64data);
        };
      };
      mediaRecorder.current.start();
      setRecording(true);
    } catch (err) {
      console.error("Mic access denied", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setRecording(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = { 
        channel, 
        consent_ack: consentAck, 
        location_text: locationText,
        language_hint: lang === 'en' || lang === 'hi' || lang === 'mr' || lang === 'pt' ? lang : undefined
      };
      if (channel === 'text') {
        payload.text = text;
      } else {
        payload.audio_base64 = audioBase64;
      }
      
      const res = await create(payload);
      router.push(`/user/request/${res.request_id}`);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-surface p-6">
      <div className="max-w-2xl mx-auto bg-surface-container rounded-xl p-6">
        <h1 className="text-2xl font-bold mb-6">{t('newReq')}</h1>
        
        {error && <div className="bg-error-container text-on-error-container p-4 rounded mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex gap-4">
            <button type="button" onClick={() => setChannel('text')} className={`flex-1 py-2 rounded-lg font-medium ${channel === 'text' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>Text</button>
            <button type="button" onClick={() => setChannel('voice')} className={`flex-1 py-2 rounded-lg font-medium ${channel === 'voice' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>Voice</button>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">{t('loc')}</label>
            <input type="text" value={locationText} onChange={(e) => setLocationText(e.target.value)} className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2" required />
          </div>

          {channel === 'text' ? (
            <div>
              <label className="block text-sm font-medium mb-1">{t('desc')}</label>
              <textarea value={text} onChange={(e) => setText(e.target.value)} className="w-full h-32 bg-surface-container-low border border-outline-variant rounded-lg p-2" required={channel==='text'}></textarea>
            </div>
          ) : (
            <div className="p-4 border border-outline-variant rounded-lg flex flex-col items-center">
              <button type="button" onPointerDown={startRecording} onPointerUp={stopRecording} onPointerLeave={stopRecording} className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-bold ${recording ? 'bg-error animate-pulse' : 'bg-primary'}`}>
                {recording ? 'Recording' : 'Hold to Record'}
              </button>
              {audioBase64 && <p className="mt-2 text-sm text-secondary">Audio captured successfully.</p>}
            </div>
          )}

          <div className="flex items-center gap-2">
            <input type="checkbox" id="consent" checked={consentAck} onChange={(e) => setConsentAck(e.target.checked)} required />
            <label htmlFor="consent" className="text-sm">{t('consent')}</label>
          </div>

          <button type="submit" disabled={loading || (channel==='voice' && !audioBase64) || !consentAck} className="w-full bg-primary-container text-on-primary py-3 rounded-lg font-semibold disabled:opacity-50">
            {loading ? t('submitting') : t('submit')}
          </button>
        </form>
      </div>
    </div>
  );
}
