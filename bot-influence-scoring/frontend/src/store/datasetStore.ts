import { create } from 'zustand';

export type DatasetId = 'cresci-2017' | 'mgtab';

interface DatasetStore {
  activeDataset: DatasetId;
  setDataset: (d: DatasetId) => void;
}

export const useDatasetStore = create<DatasetStore>((set) => ({
  activeDataset: 'cresci-2017',
  setDataset: (d) => set({ activeDataset: d }),
}));
