'use client';
import {useEffect,useState} from 'react';
export default function PrivateImage({applicationId,index}:{applicationId:string;index:number}){
 const [url,setUrl]=useState(''),[error,setError]=useState('');
 useEffect(()=>{let active=true;let objectUrl='';fetch(`${process.env.NEXT_PUBLIC_API_URL||'/api'}/applications/${applicationId}/screenshots/${index}`,{headers:{Authorization:`Bearer ${localStorage.getItem('token')}`}}).then(async r=>{if(!r.ok)throw new Error('Screenshot unavailable');objectUrl=URL.createObjectURL(await r.blob());if(active)setUrl(objectUrl)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false;if(objectUrl)URL.revokeObjectURL(objectUrl)}},[applicationId,index]);
 if(error)return <p role="status">{error}</p>;return url?<a href={url} target="_blank" rel="noreferrer"><img src={url} alt={`Application screenshot ${index+1}`} className="w-full rounded-lg"/></a>:<p>Loading screenshot…</p>
}
