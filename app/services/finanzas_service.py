# app/services/finanzas_service.py
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.proyecto import Proyecto
from app.models.finanza import Finanza
from app.models.gasto import Gasto
from app.models.ingreso_proyecto import IngresoProyecto # New Import
from app.database.db import get_session

class FinanzasService:
    def __init__(self, session: Session = None):
        self.session = session if session else get_session()

    def _get_project_income(self, project_id: int, start_date: date = None, end_date: date = None) -> float:
        # User clarification: "Los ingresos son los anticipos" + additional project incomes
        project_anticipo_query = self.session.query(Proyecto.anticipo).filter(
            Proyecto.id == project_id
        )
        # Applying date filters to anticipo based on project's start date
        if start_date:
            project_anticipo_query = project_anticipo_query.filter(Proyecto.fecha_inicio >= start_date)
        if end_date:
            project_anticipo_query = project_anticipo_query.filter(Proyecto.fecha_inicio <= end_date)
        
        anticipo_amount = project_anticipo_query.scalar()
        anticipo_amount = anticipo_amount if anticipo_amount is not None else 0.0

        # Sum additional project incomes
        additional_incomes_query = self.session.query(func.sum(IngresoProyecto.cantidad)).filter(
            IngresoProyecto.proyecto_id == project_id
        )
        if start_date:
            additional_incomes_query = additional_incomes_query.filter(IngresoProyecto.fecha >= start_date)
        if end_date:
            additional_incomes_query = additional_incomes_query.filter(IngresoProyecto.fecha <= end_date)
        
        additional_incomes_amount = additional_incomes_query.scalar()
        additional_incomes_amount = additional_incomes_amount if additional_incomes_amount is not None else 0.0

        return anticipo_amount + additional_incomes_amount

    def _get_project_expenses(self, project_id: int, start_date: date = None, end_date: date = None) -> float:
        query = self.session.query(func.sum(Gasto.cantidad)).filter(
            Gasto.proyecto_id == project_id
        )
        if start_date:
            query = query.filter(Gasto.fecha >= start_date)
        if end_date:
            query = query.filter(Gasto.fecha <= end_date)
        
        expenses = query.scalar()
        return expenses if expenses is not None else 0.0
    
    def _get_company_total_project_expenses(self, start_date: date = None, end_date: date = None) -> float:
        query = self.session.query(func.sum(Gasto.cantidad))
        if start_date:
            query = query.filter(Gasto.fecha >= start_date)
        if end_date:
            query = query.filter(Gasto.fecha <= end_date)
        
        expenses = query.scalar()
        return expenses if expenses is not None else 0.0

    def _get_company_income(self, start_date: date = None, end_date: date = None) -> float:
        # User clarification: "Los ingresos son los anticipos" + additional project incomes
        total_anticipos_query = self.session.query(func.sum(Proyecto.anticipo))
        if start_date:
            total_anticipos_query = total_anticipos_query.filter(Proyecto.fecha_inicio >= start_date)
        if end_date:
            total_anticipos_query = total_anticipos_query.filter(Proyecto.fecha_inicio <= end_date)
        total_anticipos = total_anticipos_query.scalar()
        total_anticipos = total_anticipos if total_anticipos is not None else 0.0

        total_additional_incomes_query = self.session.query(func.sum(IngresoProyecto.cantidad))
        if start_date:
            total_additional_incomes_query = total_additional_incomes_query.filter(IngresoProyecto.fecha >= start_date)
        if end_date:
            total_additional_incomes_query = total_additional_incomes_query.filter(IngresoProyecto.fecha <= end_date)
        total_additional_incomes = total_additional_incomes_query.scalar()
        total_additional_incomes = total_additional_incomes if total_additional_incomes is not None else 0.0
        
        return total_anticipos + total_additional_incomes

    def _get_company_egresos_generales(self, start_date: date = None, end_date: date = None) -> float:
        # This still represents non-project specific 'egresos' from the Finanza table
        query = self.session.query(func.sum(Finanza.monto)).filter(Finanza.tipo == 'egreso')
        if start_date:
            query = query.filter(Finanza.fecha >= start_date)
        if end_date:
            query = query.filter(Finanza.fecha <= end_date)
        egresos = query.scalar()
        return egresos if egresos is not None else 0.0

    def get_all_projects(self):
        return self.session.query(Proyecto).all()
    
    def get_project_by_id(self, project_id: int):
        return self.session.query(Proyecto).filter(Proyecto.id == project_id).first()

    def get_company_general_balance(self, start_date: date = None, end_date: date = None):
        total_income = self._get_company_income(start_date, end_date)
        total_project_expenses = self._get_company_total_project_expenses(start_date, end_date)
        total_general_egresos = self._get_company_egresos_generales(start_date, end_date)
        
        total_expenses = total_project_expenses + total_general_egresos
        profit = total_income - total_expenses
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "profit": profit
        }

    def get_project_profitability(self, project_id: int, start_date: date = None, end_date: date = None):
        project_income = self._get_project_income(project_id, start_date, end_date)
        project_expenses = self._get_project_expenses(project_id, start_date, end_date)

        profit = project_income - project_expenses
        return {
            "project_income": project_income,
            "project_expenses": project_expenses,
            "profit": profit
        }

    def get_top_profitable_projects(self, limit: int = 3, start_date: date = None, end_date: date = None):
        projects = self.get_all_projects()
        profitabilities = []
        for project in projects:
            # Only consider projects whose start date falls within the filter range for top profitable projects
            if (start_date is None or project.fecha_inicio >= start_date) and \
               (end_date is None or project.fecha_inicio <= end_date):
                profit_data = self.get_project_profitability(project.id, start_date, end_date)
                profitabilities.append({
                    "proyecto": project,
                    "profit": profit_data["profit"]
                })
        
        profitabilities.sort(key=lambda x: x["profit"], reverse=True)
        return profitabilities[:limit]

    def get_expenses_by_description(self, description_keyword: str, project_id: int = None, start_date: date = None, end_date: date = None):
        query = self.session.query(func.sum(Gasto.cantidad)).filter(
            Gasto.descripcion.ilike(f"%{description_keyword}%")
        )
        if project_id:
            query = query.filter(Gasto.proyecto_id == project_id)
        if start_date:
            query = query.filter(Gasto.fecha >= start_date)
        if end_date:
            query = query.filter(Gasto.fecha <= end_date)
        
        total_amount = query.scalar()
        return total_amount if total_amount is not None else 0.0

    def close_session(self):
        self.session.close()