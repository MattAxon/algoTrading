import React from 'react'

export default function Strategies() {
  const links = [
    {
      name: 'Equal Weight S&P 500',
      address: './SP500'
    },
    {
      name: 'Momentum Trading Strategy',
      address: './Momentum'
    },
    {
      name: 'Value Picking Strategy',
      address: './ValuePicking'
    }
  ]
  return (

    <div>
      <h2 className='text-center text-xl text-white'>Trading Strategies</h2>
      <hr className='w-96 mx-auto mt-2' />
      {links.map((link, index) => {
        return (
          <div className='mt-5' key={index}>
            <h3 className='text-center  text-white'>
              <a className='hover:text-slate-400' href={link.address}>
                {link.name}
              </a>
            </h3>
          </div>)
      })}</div>
  )
}
