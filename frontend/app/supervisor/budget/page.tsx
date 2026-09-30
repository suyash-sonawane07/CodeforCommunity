'use client';
import { useState } from 'react';
import { useSimulation } from '@/hooks';

export default function BudgetPage() {
  const { simulate, loading, result } = useSimulation();
  const [roads, setRoads] = useState('100000');
  const [water, setWater] = useState('150000');
  const [health, setHealth] = useState('50000');
  const [education, setEducation] = useState('200000');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    simulate({
      roads: parseFloat(roads) || 0,
      water: parseFloat(water) || 0,
      health: parseFloat(health) || 0,
      education: parseFloat(education) || 0,
    });
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="bg-surface-container p-6 rounded-xl shadow-sm">
        <h2 className="text-xl font-bold mb-4">Policy Simulator</h2>
        <p className="text-sm text-on-surface-variant mb-6">Allocate budget to sectors to see how many demand clusters can be covered.</p>
        
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Roads Budget (₹)</label>
            <input type="number" value={roads} onChange={e => setRoads(e.target.value)} className="w-full bg-surface-container-low border border-outline rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Water Budget (₹)</label>
            <input type="number" value={water} onChange={e => setWater(e.target.value)} className="w-full bg-surface-container-low border border-outline rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Health Budget (₹)</label>
            <input type="number" value={health} onChange={e => setHealth(e.target.value)} className="w-full bg-surface-container-low border border-outline rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Education Budget (₹)</label>
            <input type="number" value={education} onChange={e => setEducation(e.target.value)} className="w-full bg-surface-container-low border border-outline rounded p-2" />
          </div>
          
          <div className="col-span-2 pt-4 border-t border-outline-variant">
            <button type="submit" disabled={loading} className="w-full bg-primary text-on-primary py-3 rounded-lg font-bold">
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </form>
      </div>

      {result && (
        <div className="bg-surface-container p-6 rounded-xl shadow-sm border border-primary-container">
          <h2 className="text-xl font-bold mb-4">Simulation Results</h2>
          <div className="flex gap-8 mb-4">
            <div>
              <p className="text-sm text-on-surface-variant">Clusters Covered Before</p>
              <p className="text-2xl font-bold">{result.coverable_clusters_before ?? 0}</p>
            </div>
            <div>
              <p className="text-sm text-on-surface-variant">Clusters Covered After</p>
              <p className="text-2xl font-bold text-primary">{result.coverable_clusters_after ?? 0}</p>
            </div>
          </div>
          <p className="text-xs text-error font-medium">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
