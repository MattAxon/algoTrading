import React from 'react'
import Head from 'next/head'
import fs from 'fs'
import Image from 'next/image'
export default function strategy({ data, strategy }) {
    const handleSubmit = async (event) => {
        event.preventDefault()
        const portfolioSize = event.target.portfolioSize.value;
        const emailTo = event.target.emailTo.value
        let url = data.url
        url = url + "?portfolioSize=" + portfolioSize + "&emailTo=" + emailTo;
        try { const res = await fetch(url) }
        catch { console.log('sucsess') }

    }
    var strat = strategy
    if (strat == 'SP500') {
        strat = 'S&P 500'
    }
    return (
        <div>
            <div className='text-white text-center'>
                <h1 className='pb-8'>{strat}</h1>
                {data.image == '/images/SP500.png' ? <Image className='mt-4' height={300} width={600} src={data.image} /> : <Image className='' height={190} width={875} src={data.image} />}

                <h2 className='mx-8 md:mx-20'>{data.description}</h2>
                <form className='my-4  py-6 rounded-sm mx-auto md:w-1/2 w-10/12 bg-neutral-700' onSubmit={handleSubmit}>
                    <span className='items-center mx-auto flex lg:flex-none'>
                        <div className='md:flex mx-auto'>
                            <div className=' mt-4'>
                                <label htmlFor='portfolioSize'>Portfolio Size: </label>
                                <input className='text-black' autoComplete='1000000' required type='number' placeholder='Portfolio Size' id='portfolioSize' />
                            </div>
                            <div className='mt-4'>
                                <label className='ml-8' htmlFor='emailTo'>Email To: </label>
                                <input className='text-black' type={'email'} required placeholder='Email To' id='emailTo' />
                            </div>
                        </div>
                    </span>
                    <button className='rounded-sm mt-8 py-2 px-4 bg-slate-600 hover:bg-slate-500' type='submit'>Execute</button>
                </form>
            </div>
        </div>
    )
}

export const getStaticPaths = async () => {
    const files = fs.readdirSync('strategyData');
    const paths = files.map((filename) => ({
        params: {
            strategy: filename.replace(".json", ""),
        }
    }));
    return {
        paths,
        fallback: false,
    };
}

export const getStaticProps = async ({ params: { strategy } }) => {
    const data = require('../strategyData/' + strategy + '.json');
    return {
        props: {
            data,
            strategy,
        }
    }
}
