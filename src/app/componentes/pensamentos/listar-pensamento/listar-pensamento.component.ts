import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-listar-pensamento',
  templateUrl: './listar-pensamento.component.html',
  styleUrl: './listar-pensamento.component.css',
})
export class ListarPensamentoComponent implements OnInit {
  pensamentos = [
    {
      id: '1',
      quote: 'Minha primeira frase, listar-pensamento.ts',
      author: 'André Guimarães',
      notifiable: true,
      createdWhen: new Date(),
    },
    {
      id: '2',
      quote: 'Minha segunda frase, listar-pensamento.ts',
      author: 'André Guimarães',
      notifiable: true,
      createdWhen: new Date(),
    },
    {
      id: '3',
      quote: 'Minha terceira frase, listar-pensamento.ts',
      author: 'André Guimarães',
      notifiable: true,
      createdWhen: new Date(),
    },
    {
      id: '4',
      quote: 'Minha quarta frase, listar-pensamento.ts',
      author: 'André Guimarães',
      notifiable: true,
      createdWhen: new Date(),
    },
  ];

  constructor() {}
  ngOnInit(): void {}
}
