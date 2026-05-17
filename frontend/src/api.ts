const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type Game = {
  id: string;
  status: "pending" | "processing" | "complete" | "failed";
  result: string | null;
  moves: number | null;
  blunders: number;
  mistakes: number;
  inaccuracies: number;
  white_player: string | null;
  black_player: string | null;
  report_summary: string | null;
  error_message: string | null;
  created_at: string;
};

export type MoveEvaluation = {
  ply: number;
  san: string;
  fen: string;
  eval_cp: number;
  classification: string;
  best_move_uci: string | null;
  best_move_san: string | null;
};

export type GameReport = {
  summary: string;
  critical_moments: Array<{
    ply: number;
    move_number: number;
    side: string;
    san: string;
    fen: string;
    eval_cp: number;
    classification: string;
    best_move_uci: string | null;
    best_move_san: string | null;
    coach_note: string;
  }>;
  opening_review: string;
  middlegame_review: string;
  endgame_review: string;
  action_plan: string[];
  metadata: {
    white_player: string;
    black_player: string;
    result: string | null;
    total_plies: number;
    blunders: number;
    mistakes: number;
    inaccuracies: number;
    source: string;
    source_detail: string | null;
  };
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  const token = localStorage.getItem("token");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    if (response.status === 401) {
      localStorage.removeItem("token");
      window.dispatchEvent(new Event("auth-error"));
    }
    throw new Error(body?.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function uploadGame(file: File): Promise<Game> {
  const formData = new FormData();
  formData.append("file", file);
  return request<Game>("/api/v1/games", { method: "POST", body: formData });
}

export function fetchGames(): Promise<Game[]> {
  return request<Game[]>("/api/v1/games");
}

export function analyzeGame(gameId: string): Promise<Game> {
  return request<Game>(`/api/v1/games/${gameId}/analyze`, { method: "POST" });
}

export function fetchReport(gameId: string): Promise<GameReport> {
  return request<GameReport>(`/api/v1/games/${gameId}/report`);
}

export function fetchMoves(gameId: string): Promise<MoveEvaluation[]> {
  return request<MoveEvaluation[]>(`/api/v1/games/${gameId}/moves`);
}

export function fetchGame(gameId: string): Promise<Game> {
  return request<Game>(`/api/v1/games/${gameId}`);
}

/**
 * Polls GET /games/{id} every `intervalMs` until status is no longer "processing".
 * Calls `onProgress` on each poll tick.
 * Rejects after `timeoutMs` (default 5 minutes).
 */
export function pollUntilComplete(
  gameId: string,
  onProgress: (game: Game) => void,
  intervalMs = 2000,
  timeoutMs = 300_000,
): Promise<Game> {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;
    const tick = async () => {
      try {
        const game = await fetchGame(gameId);
        onProgress(game);
        if (game.status !== "processing") {
          resolve(game);
          return;
        }
        if (Date.now() > deadline) {
          reject(new Error("Analysis timed out after 5 minutes."));
          return;
        }
        setTimeout(tick, intervalMs);
      } catch (err) {
        reject(err);
      }
    };
    setTimeout(tick, intervalMs);
  });
}

export function login(data: any): Promise<{ access_token: string }> {
  return request<{ access_token: string }>("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function register(data: any): Promise<{ access_token: string }> {
  return request<{ access_token: string }>("/api/v1/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function getMe(): Promise<any> {
  return request<any>("/api/v1/users/me");
}
