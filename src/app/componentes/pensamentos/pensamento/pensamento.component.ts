import { Pensamento } from './../pensamento';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-pensamento',
  templateUrl: './pensamento.component.html',
  styleUrl: './pensamento.component.css',
})
export class PensamentoComponent implements OnInit {
  pensamento = {
    id: '1',
    quote: 'Minha primeira frase, pensamento.ts',
    author: 'André Guimarães',
    notifiable: true,
    createdWhen: new Date(),
  };

  constructor() {}
  ngOnInit(): void {}
}
