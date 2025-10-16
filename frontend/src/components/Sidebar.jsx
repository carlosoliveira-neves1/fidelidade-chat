// frontend/src/components/Sidebar.jsx
import React from "react";
import { NavLink } from "react-router-dom";

/**
 * Sidebar da aplicação.
 * - Lê o usuário do localStorage (chave "cdc_user")
 * - Esconde o item "Admin" quando user.role !== "ADMIN"
 * - Usa NavLink (React Router v6) para estilizar link ativo
 */
export default function Sidebar() {
  // Recupera usuário salvo ao logar
  const user = (() => {
    try {
      return JSON.parse(localStorage.getItem("cdc_user") || "null");
    } catch {
      return null;
    }
  })();

  const linkBase =
    "block px-4 py-3 rounded-xl text-[15px] transition hover:bg-[#f3ebe7] hover:text-[#91231d]";
  const linkActive =
    "bg-[#f8f2ef] text-[#91231d] font-semibold shadow-sm border border-[#f1e6e0]";

  const renderLink = (to, label) => (
    <NavLink
      key={to}
      to={to}
      className={({ isActive }) =>
        [linkBase, isActive ? linkActive : "text-[#3b3b3b]"].join(" ")
      }
      end={to === "/"}
    >
      {label}
    </NavLink>
  );

  return (
    <aside
      className="min-h-screen w-[220px] bg-[#fff8ef] border-r border-[#f1e6e0] flex flex-col"
      style={{ padding: "16px 12px" }}
    >
      {/* Cabeçalho / Marca */}
      <div className="flex items-center gap-3 mb-6 px-2">
        {/* Se tiver arquivo em /public/cdc-logo.png ele aparece; senão, fica só o texto */}
        <img
          src="/cdc-logo.png"
          alt="Casa do Cigano"
          width={34}
          height={34}
          onError={(e) => (e.currentTarget.style.display = "none")}
        />
        <div>
          <div className="text-[18px] font-semibold text-[#c22f27] leading-5">
            Fidelidade
          </div>
          {user?.role && (
            <div className="text-[12px] text-[#9b6e64] mt-[2px]">
              {user.role} {user?.store_id ? "· Loja" : "· Todas"}
            </div>
          )}
        </div>
      </div>

      {/* Navegação */}
      <nav className="flex flex-col gap-1">
        {renderLink("/", "Dashboard")}
        {renderLink("/clientes", "Clientes")}
        {renderLink("/visitas", "Visitas")}
        {renderLink("/resgates", "Resgates")}

        {/* Só exibe Admin para ADMIN */}
        {user?.role === "ADMIN" && renderLink("/admin", "Admin")}
      </nav>

      {/* Rodapé / Espaçador */}
      <div className="mt-auto text-[12px] text-[#9b6e64] px-3 pt-6">
        Casa do Cigano ©
      </div>
    </aside>
  );
}
