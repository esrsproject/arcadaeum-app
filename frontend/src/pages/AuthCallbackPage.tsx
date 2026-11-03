import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AuthCallbackPage() {
	const navigate = useNavigate();

	useEffect(() => {
		const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
		void fetch(`${apiUrl}/auth/oauth/google/exchange`, {
			method: "POST",
			credentials: "include",
		})
			.then(async (response) => {
				if (!response.ok) throw new Error("Google sign-in exchange failed");
				return (await response.json()) as { access_token: string };
			})
			.then(({ access_token }) => {
				localStorage.setItem("access_token", access_token);
				navigate("/user", { replace: true });
			})
			.catch(() => navigate("/signin", { replace: true }));
	}, [navigate]);

	return <div>Signing you in...</div>;
}
