import { create } from 'zustand';

export interface UserFavorite {
  id: string;
  code: string;
  type: 'KPI' | 'DASHBOARD' | 'REPORT' | 'INITIATIVE' | 'DECISION';
  title: string;
  route: string;
}

interface FavoritesState {
  favorites: UserFavorite[];
  toggleFavorite: (item: UserFavorite) => void;
  isFavorite: (id: string) => boolean;
}

export const useFavoritesStore = create<FavoritesState>((set, get) => ({
  favorites: [
    {
      id: 'fav-kpi-1',
      code: 'ARR-01',
      type: 'KPI',
      title: 'Net ARR & Expansion Growth',
      route: '/metrics',
    },
    {
      id: 'fav-dec-42',
      code: 'DEC-042',
      type: 'DECISION',
      title: 'Southeastern Carrier Reallocation',
      route: '/governance',
    },
  ],
  toggleFavorite: (item) => {
    const { favorites } = get();
    const exists = favorites.some((f) => f.id === item.id);
    if (exists) {
      set({ favorites: favorites.filter((f) => f.id !== item.id) });
    } else {
      set({ favorites: [...favorites, item] });
    }
  },
  isFavorite: (id) => get().favorites.some((f) => f.id === id),
}));
