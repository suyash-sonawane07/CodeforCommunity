import { useState, useEffect } from 'react';
import { translations } from '../lib/i18n';

export function useTranslation() {
  const [lang, setLang] = useState('en');

  useEffect(() => {
    const savedLang = localStorage.getItem('lang');
    if (savedLang) setLang(savedLang);
  }, []);

  const changeLang = (newLang: string) => {
    setLang(newLang);
    localStorage.setItem('lang', newLang);
  };

  const t = (key: string) => {
    return translations[lang]?.[key] || translations['en'][key] || key;
  };

  return { lang, changeLang, t };
}
