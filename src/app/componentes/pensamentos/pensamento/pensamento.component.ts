import { Pensamento } from './../pensamento';
import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-pensamento',
  templateUrl: './pensamento.component.html',
  styleUrl: './pensamento.component.css',
})
export class PensamentoComponent implements OnInit {
  @Input() pensamento = {
    id: '1',
    quote: 'Minha primeira frase, pensamento.ts',
    author: 'André Guimarães',
    notifiable: true,
    createdWhen: new Date(),
  };

  constructor() {}
  ngOnInit(): void {}
}
